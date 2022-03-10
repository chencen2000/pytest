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
pip install click
pyinstaller pyideviceutil.py
cp tools_x64.tar.gz tools.tar.gz
pyinstaller --add-data "tools.tar.gz:." iOS_installer.py 
x86
pip install click
pyinstaller pyideviceutil.py
cp tools_x32.tar.gz tools.tar.gz
pyinstaller --add-data "tools.tar.gz:." iOS_installer.py 

usage:
iOS_installer config <path to config.json> --udid <udid>
return:
0, success
1, error
2, device not found 
3, device not trusted

config.json
{
    "wifi":[
        {
            "ssid": "ssid_name",
            "password": "wifi_password"
        },
        {
            "ssid": "gg",
            "password": "12345678"
        }
    ],
    "app":[
        "/home/qa/Downloads/RADI_1.50.6.a1.ipa",
        "full path to app2"
    ]
}
"wifi": add wifi information, "ssid" and "password".
"app": add full path of ipa