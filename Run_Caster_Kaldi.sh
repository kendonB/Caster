echo Running Kaldi from Dragonfly CLI

cd ~/caster

CASTER_USER_DIR=%DROPBOX%/caster_ubuntu_user /usr/bin/python3 -m dragonfly load _*.py --engine kaldi  --no-recobs-messages

pause 1
