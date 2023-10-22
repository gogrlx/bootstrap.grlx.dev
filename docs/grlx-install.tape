# Where should we write the GIF?
Output grlx-install.gif
# Set up a 1200x600 terminal with 46px font.
Set FontSize 30
Set Width 1500
Set Height 600
# replace 'linux' with darwin if you're on macOS
Type "curl -L https://releases.grlx.dev/linux/amd64/latest/grlx > grlx"
Enter
Hide
Sleep 45s
Show
Sleep 1s
Type "chmod +x grlx"
Enter
Type "./grlx init"
Enter
Sleep 5s
Type "localhost"
Enter
Sleep 50ms
Enter
Sleep 50ms
Enter
Sleep 50ms
Enter
Sleep 2s
Type "# save this key for later"
Enter
Sleep 5s

