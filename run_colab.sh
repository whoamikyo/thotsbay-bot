#!/bin/sh
# Install dependencies
sudo apt update
sudo apt-get install python3.9
sudo apt install python3.9-distutils
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 2
sudo update-alternatives --set python3 /usr/bin/python3.9
sudo apt-get install -y ffmpeg
sudo apt install python3-pip
python -m pip install --upgrade pip
pip install setuptools --upgrade
pip install -q --pre poetry
#curl -sSL https://install.python-poetry.org | python3 -
#curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
# aws config
curl https://rclone.org/install.sh | sudo bash
# Git clone
git clone https://github.com/whoamikyo/thotsbay-bot
cp /content/drive/MyDrive/conf/.env /content/thotsbay-bot/.env
mkdir -p ~/.config/rclone
cp /content/drive/MyDrive/conf/rclone.conf ~/.config/rclone/rclone.conf
git config --global user.name 'github-actions[bot]'
git config --global user.email 'github-actions[bot]@users.noreply.github.com'
cp /content/drive/MyDrive/conf/config /content/thotsbay-bot/.git/config
# Run main.py
cd ./thotsbay-bot/
#pipenv shell
poetry install --no-interaction --without dev
poetry run python main.py
# Git commit
#git add -A
#git commit -m "Auto-update"
# finally push
#git push