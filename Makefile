
dep:
	sudo apt-get install python3-virtualenv python3-dev python3-pil.imagetk python3-tk

env:
	virtualenv --system-site-packages -p /usr/bin/python3 env 
	#env/bin/pip3 install -r requirements-dev.txt
	#env/bin/pip3 install -r requirements.txt
