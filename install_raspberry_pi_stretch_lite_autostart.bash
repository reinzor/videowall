#!/usr/bin/env bash

# Install system dependencies
sudo apt-get -y update
sudo apt-get -y install git \
                        libgstreamer-plugins-base1.0-dev \
                        gstreamer1.0-plugins-base-apps \
                        gstreamer1.0-tools \
                        gstreamer1.0-plugins-good \
                        gstreamer1.0-plugins-bad \
                        python-pip

# Install python dependencies
sudo -H pip install -r requirements.txt

# Build & Install Gstreamer MMAL
git clone https://github.com/reinzor/gst-mmal /tmp/gst-mmal
cd /tmp/gst-mmal
LDFLAGS='-L/opt/vc/lib' CPPFLAGS='-I/opt/vc/include -I/opt/vc/include/interface/vcos/pthreads -I/opt/vc/include/interface/vmcs_host/linux' ./autogen.sh --disable-gtk-doc
make
sudo make install

# Build & Install Gstreamer OMX
git clone https://github.com/reinzor/gst-omx /tmp/gst-omx
cd /tmp/gst-omx
git checkout 1.10.4
LDFLAGS='-L/opt/vc/lib' CFLAGS='-I/opt/vc/include -I/opt/vc/include/IL -I/opt/vc/include/interface/vcos/pthreads -I/opt/vc/include/interface/vmcs_host/linux -I/opt/vc/include/IL' CPPFLAGS='-I/opt/vc/include -I/opt/vc/include/IL -I/opt/vc/include/interface/vcos/pthreads -I/opt/vc/include/interface/vmcs_host/linux -I/opt/vc/include/IL' ./autogen.sh --disable-gtk-doc --with-omx-target=rpi
make
sudo make install

# Create videos folder and download sample video
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
wget https://github.com/reinzor/videowall/releases/download/0/big_buck_bunny_720p_30mb.mp4 -O $SCRIPT_DIR/videos/videos/big_buck_bunny_720p_30mb.mp4

# Setup paths in bashrc
echo "source $SCRIPT_DIR/setup.bash" >> ~/.bashrc

# Copy additional raspberry pi system files
sudo rm /etc/network/mac
sudo cp -r $SCRIPT_DIR/cfg/rpi/* /

# Enable startup run
sudo systemctl daemon-reload
sudo systemctl enable videowall

# Show installation done message
echo "======="
echo ""
echo "Installation complete, please source your ~/.bashrc and type the following command:"
echo ""
echo " gst-launch-1.0 -v filesrc location=$SCRIPT_DIR/videos/big_buck_bunny_720p_30mb.mp4 ! qtdemux ! h264parse ! omxh264dec ! videocrop bottom=10 ! mmalvideosink"
echo ""
echo "======"
