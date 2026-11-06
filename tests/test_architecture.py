"""Check release selection without downloading or modifying the host."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURES = {
    "x86_64": "amd64",
    "i686": "386",
    "i386": "386",
    "aarch64": "arm64",
    "arm64": "arm64",
    "armv8": "arm64",
    "armv7l": "arm",
}


class ArchitectureTests(unittest.TestCase):
    def run_installer(self, version, component, architecture):
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            binary_dir = sandbox / "usr/local/bin"
            binary_dir.mkdir(parents=True)
            config = sandbox / "etc/grlx"
            config.mkdir(parents=True)
            (config / component).write_text("existing config\n")
            mocks = sandbox / "mocks"
            mocks.mkdir()
            for name, body in {
                "uname": 'printf "%s\\n" "$TEST_ARCH"',
                "curl": 'printf "%s\\n" "$*" > "$DOWNLOAD_LOG"\nexit 22',
                "systemctl": 'printf "%s\\n" "$*" > "$SERVICE_LOG"\nexit 1',
            }.items():
                executable = mocks / name
                executable.write_text(f"#!/bin/bash\n{body}\n")
                executable.chmod(0o755)
            script = (ROOT / version / component).read_text()
            for prefix in ("/usr/local/bin", "/etc/grlx"):
                script = script.replace(prefix, str(sandbox) + prefix)
            download_log = sandbox / "download"
            result = subprocess.run(
                ["bash"],
                check=False,
                input=script,
                text=True,
                capture_output=True,
                timeout=10,
                env={
                    **os.environ,
                    "PATH": f"{mocks}:{os.environ['PATH']}",
                    "UNINSTALL": "",
                    "TEST_ARCH": architecture,
                    "DOWNLOAD_LOG": str(download_log),
                    "SERVICE_LOG": str(sandbox / "services"),
                },
            )
            self.assertFalse((sandbox / "services").exists())
            self.assertEqual(list(binary_dir.iterdir()), [])
            return result, download_log.read_text() if download_log.exists() else None

    def test_supported_architectures_select_release(self):
        for version in ("latest", "v1.0.5"):
            for component in ("farmer", "sprout"):
                for architecture, release in ARCHITECTURES.items():
                    with self.subTest(
                        version=version, component=component, architecture=architecture
                    ):
                        result, download = self.run_installer(
                            version, component, architecture
                        )
                        self.assertEqual(result.returncode, 22, result.stderr)
                        self.assertIsNotNone(download)
                        self.assertEqual(
                            download.split()[-1],
                            f"https://artifacts.grlx.dev/linux/{release}/v1.0.5/{component}",
                        )

    def test_unsupported_architectures_fail_before_download(self):
        for version in ("latest", "v1.0.5"):
            for component in ("farmer", "sprout"):
                for architecture in ("riscv64", "", "x86_64-extra"):
                    with self.subTest(
                        version=version, component=component, architecture=architecture
                    ):
                        result, download = self.run_installer(
                            version, component, architecture
                        )
                        self.assertEqual(result.returncode, 1, result.stderr)
                        self.assertIn("Unknown machine architecture:", result.stdout)
                        self.assertIsNone(download)


if __name__ == "__main__":
    unittest.main()
