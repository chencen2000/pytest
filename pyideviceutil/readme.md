dev env setup
apt-get install python3-pip
apt-get install python3-setuptools
apt-get install python3-venv
apt install git
apt install snapd
snap install code --classic

in venv
pip3 install --upgrade pip 
pip3 install setuptools-rust
pip3 install pymobiledevice3
pip3 install pyinstaller

publish
pyinstaller pyideviceutil.py