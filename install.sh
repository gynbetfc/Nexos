#!/data/data/com.termux/files/usr/bin/bash

clear

echo "[NEXOS INSTALL]"

pkg update -y
pkg install python git termux-api -y

pip install websockets requests

mkdir -p ~/.nexos

cd ~/.nexos || exit

git clone https://github.com/gynbetfc/Nexos

cd Nexos/agent || exit

echo "alias nexos-start='cd ~/.nexos/Nexos/agent && nohup python main.py > /dev/null 2>&1 &'" >> ~/.bashrc

echo "alias nexos-stop='pkill -f main.py'" >> ~/.bashrc

source ~/.bashrc

termux-wake-lock

nohup python main.py > /dev/null 2>&1 &

echo "NEXOS INSTALLED"
