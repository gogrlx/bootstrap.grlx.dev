Output grlx-cmd.gif
Set FontSize 30
Set Width 1500
Set Height 600
Type "./grlx keys accept -A"
Sleep 3
Enter
Sleep 3
Enter
Sleep 3
Enter
Sleep 1
Type "./grlx -T \* test ping"
Sleep 2
Enter
Sleep 4
Type "./grlx -T \* cmd run whoami"
Sleep 2
Enter
Sleep 4
Type "./grlx -T \* cmd run --out json -- uname -a | jq"
Sleep 3
Enter
Sleep 4
