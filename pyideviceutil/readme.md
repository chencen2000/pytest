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
x64
cp tools_x64.tar.gz tools.tar.gz
pyinstaller --add-data "tools.tar.gz:." iOS_installer.py 
x86
cp tools_x32.tar.gz tools.tar.gz
pyinstaller --add-data "tools.tar.gz:." iOS_installer.py 