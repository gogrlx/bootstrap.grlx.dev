"""Run installers against fake host paths; never modify host services or files."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DownloadTests(unittest.TestCase):
    def test_failed_download_preserves_installation(self):
        for version in ("latest", "v1.0.5"):
            for component in ("farmer", "sprout"):
                with self.subTest(version=version, component=component):
                    with tempfile.TemporaryDirectory() as directory:
                        sandbox = Path(directory)
                        binary_dir = sandbox / "usr/local/bin"
                        binary_dir.mkdir(parents=True)
                        config = sandbox / "etc/grlx"
                        config.mkdir(parents=True)
                        (config / component).write_text("existing config\n")
                        binary = binary_dir / f"grlx-{component}"
                        binary.write_text("existing executable\n")
                        binary.chmod(0o755)
                        mocks = sandbox / "mocks"
                        mocks.mkdir()
                        # Simulate a server that fails after sending a partial body.
                        curl = mocks / "curl"
                        curl.write_text("#!/bin/bash\nprintf partial\nexit 22\n")
                        curl.chmod(0o755)
                        systemctl = mocks / "systemctl"
                        systemctl.write_text(
                            '#!/bin/bash\nprintf "%s\\n" "$*" >> "$SERVICE_LOG"\n'
                        )
                        systemctl.chmod(0o755)
                        script = (ROOT / version / component).read_text()
                        for prefix in ("/usr/local/bin", "/etc/grlx"):
                            script = script.replace(prefix, str(sandbox) + prefix)
                        result = subprocess.run(
                            ["bash"],
                            input=script,
                            text=True,
                            capture_output=True,
                            env={
                                **os.environ,
                                "PATH": f"{mocks}:{os.environ['PATH']}",
                                "UNINSTALL": "",
                                "SERVICE_LOG": str(sandbox / "services"),
                            },
                        )
                        self.assertNotEqual(result.returncode, 0)
                        self.assertEqual(binary.read_text(), "existing executable\n")
                        self.assertEqual(binary.stat().st_mode & 0o777, 0o755)
                        self.assertFalse((sandbox / "services").exists())
                        self.assertEqual(list(binary_dir.iterdir()), [binary])


if __name__ == "__main__":
    unittest.main()
