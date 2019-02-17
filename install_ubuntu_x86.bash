#!/usr/bin/env bash

# Install system dependencies
sudo apt-get -y update
sudo apt-get -y install git \
                        gstreamer1.0-plugins-base-apps \
                        gstreamer1.0-plugins-good \
                        gstreamer1.0-plugins-bad \
                        python-pip

# Install python dependencies
sudo -H pip install -r requirements.txt

# Create videos folder and download sample video
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
wget https://github.com/reinzor/videowall/releases/download/0/big_buck_bunny_720p_30mb.mp4 -O $SCRIPT_DIR/videos/big_buck_bunny_720p_30mb.mp4

# Setup paths in bashrc
echo "source $SCRIPT_DIR/setup.bash" >> ~/.bashrc
