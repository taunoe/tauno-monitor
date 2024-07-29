<img src="https://raw.githubusercontent.com/taunoe/tauno-monitor/main/data/icons/hicolor/scalable/apps/art.taunoerik.tauno-monitor.svg" align="left">

# Tauno Monitor

The goal is to make a stand-alone simple serial port monitor for the GNOME desktop.

It aims to be beginner-friendly, small and easy to use. Not feature-rich and professional.

It remembers the last settings (Theme, Baud Rate, Port etc), auto reconnects to the serial port and can log data to a file.

## Important

Depending on your system you may need to add a user to dialout group to open serial ports:

```bash
sudo usermod -a -G dialout $USER
sudo usermod -a -G plugdev $USER
```

You may also need to install udev rules. PlatformIO have a good [instructions](https://docs.platformio.org/en/latest/core/installation/udev-rules.html)

## Screenshots

![Light mode](data/screenshots/light_new.png)

![Dark mode](data/screenshots/dark_new.png)

![About window](data/screenshots/about_new.png)

![Preferences window](data/screenshots/pref_new.png)

## Install

### Flatpak

[![Get it from the Flathub](https://dl.flathub.org/assets/badges/flathub-badge-en.png)](https://flathub.org/apps/art.taunoerik.tauno-monitor)

### Snap

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/tauno-monitor)

Ubuntu users also must enable "Access USB hardware directly" on the Ubuntu Store Software store:

![Ubuntu premissions](data/screenshots/ubuntu_access_usb_directly.png)

or from command line:

```bash
snap connect tauno-monitor:raw-usb
```

## Build

You can build Tauno Monitor using [GNOME Builder](https://flathub.org/et/apps/org.gnome.Builder): import the project and press the Play button.

## Support

<a href="https://www.buymeacoffee.com/taunoerik" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

 ___

Copyright 2023-2024 Tauno Erik https://taunoerik.art
