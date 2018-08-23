# Videowall (WIP)

Video wall with multiple tiles that enables synchronized video playback, mirrored or tiled.

## Installation

### Raspberry PI installation

#### Installation prerequisites

- Raspbian Jessie
- Raspberry Pi 3 / Raspberry Pi Zero (other Pi's not tested)
- Videowall repository is your current working directory

#### Installation dependencies

Install the `x-window-system` and `gstreamer`:

```
sudo apt-get -y install x-window-system \
                        gstreamer1.0-tools \
                        gstreamer1.0-plugins-good \
                        gstreamer1.0-plugins-bad \
                        gstreamer1.0-plugins-ugly \
                        gstreamer1.0-omx \
                        gir1.2-gst-plugins-base-1.0 \
                        python-gst-1.0 \
                        pulseaudio \
                        python-colorlog
```

Make sure `gstreamer is working properly` by downloading and playing an x264 encoded sample video:

```
wget https://www.sample-videos.com/video/mp4/720/big_buck_bunny_720p_30mb.mp4 -O ~/big_buck_bunny_720p_30mb.mp4
```

#### Set-up videowall

Enable the x-server on startup:

```
sudo cp systemd/startx/override.conf /etc/systemd/system/getty@tty1.service.d/ 
sudo systemctl daemon-reload
sudo systemctl restart getty@tty1.service
```

If everything went well, the x server should now be running and you should see a black screen with a small green font: `pi@raspberrypi`.

Add the following to `/etc/X11/xinit/xinitrc` after the first line to disable screen blanking:
```
xset s off         # don't activate screensaver
xset -dpms         # disable DPMS (Energy Star) features.
xset s noblank     # don't blank the video device
```

Set boot config RPI so we can use more GPU memory (not sure whether this has any effect):
```
echo "gpu_mem = 386MB" | sudo tee -a /boot/config.txt
```

## Quick start

### Server

    scripts/server
    
### Client

    scripts/client

## References

- [Override getty1](https://raymii.org/s/tutorials/Run_software_on_tty1_console_instead_of_login_getty.html)
- [Vigsterkr pi-wall](https://github.com/vigsterkr/pi-wall)
- [Gstreamer mmal for smooth video playback on RPI](https://gstreamer.freedesktop.org/data/events/gstreamer-conference/2016/John%20Sadler%20-%20Smooth%20video%20on%20Raspberry%20Pi%20with%20gst-mmal%20(Lightning%20Talk).pdf)
- [Gstreamer sync server for synchronized playback on multiple client with a gstreamer client server set-up](https://github.com/ford-prefect/gst-sync-server)
- [Multicast Video-Streaming on Embedded Linux Environment, Daichi Fukui, Toshiba Corporation, Japan Technical Jamboree 63, Dec 1st, 2017](https://elinux.org/images/3/33/Multicast_jamboree63_fukui.pdf)
- [omxplayer-sync](https://github.com/turingmachine/omxplayer-sync)
- [pwomxplayer](https://github.com/JeffCost/pwomxplayer)
- [dbus vlc](https://wiki.videolan.org/DBus-spec/)
- [dbus tutorial phython for MPRIS](http://amhndu.github.io/Blog/python-dbus-mpris.html)
- [dbus omxplayer](https://github.com/popcornmix/omxplayer)
- [GPU memory 90 degrees omxplayer](https://github.com/popcornmix/omxplayer/issues/467)
- [Remote dbus control](https://stackoverflow.com/questions/10158684/connecting-to-dbus-over-tcp/13275973#13275973)
