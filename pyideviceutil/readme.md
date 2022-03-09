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
pyinstaller -F pyideviceutil.py -n iDeviceUtil
pyinstaller --add-data "tools_x32.tar.gz:." --add-data "tools_x64.tar.gz:." iOS_installer.py 