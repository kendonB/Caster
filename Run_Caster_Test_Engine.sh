echo Running Test Engine from Dragonfly CLI.

echo "
Test Engine Window
--------------------------Instructions -------------------------
Type commands to emulate as if they are being dictated by voice. 
lowercase mimics \`commands\`, UPPERCASE mimics \`free dictation\`
Upper and lowercase words can be mixed e.g `say THIS IS A TEST` 

Edit the \`--delay 3\` in bat file to change command delay in seconds.
The delay allows user to switch to the relevant application to test commands
----------------------------------------------------------------

"

python3 -m dragonfly test _caster.py --delay 3

pause 1
