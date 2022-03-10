# iOS_installer

Mantis #0005706
[0005706: App load EXE for Linux (iOS) - FutureDial (mantishub.io)](https://futuredial.mantishub.io/view.php?id=5706)

## Development Setup

    apt-get install python3-pip
    apt-get install python3-setuptools
    apt-get install python3-venv
    apt install git
    apt install snapd
    snap install code --classic

## Clone the repo
    git clone https://github.com/chencen2000/pytest.git

## prepare venv

    python3 -m venv venv
    source ./venv/bin/active
    pip install --upgrade pip 
    pip install click
    pip install pyinstaller
    
## publish

### for 64-bit OS release

    cp tools_x64.tar.gz tools.tar.gz
    pyinstaller --add-data "tools.tar.gz:." -F iOS_installer.py 
    
### for 32-bit OS release

    cp tools_x32.tar.gz tools.tar.gz
    pyinstaller --add-data "tools.tar.gz:." iOS_installer.py

## Usage
iOS_installer config <path to config.json> --udid <udid>

Exit code:
0, success
1, error
2, device not found 
3, device not trusted

### config.json

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