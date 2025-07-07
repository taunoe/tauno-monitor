<img src="https://raw.githubusercontent.com/taunoe/tauno-monitor/main/data/icons/hicolor/scalable/apps/art.taunoerik.tauno-monitor.svg" align="center">

# Tauno Monitor

The serial port monitor for Arduino and other embedded development.

The goal is to make a user-friendly serial port monitor for the GNOME desktop.

### Features:

 - Remembers the last used settings (Theme, Baud Rate, Port, etc.)
 - Auto reconnects to the serial port when the connection is lost
 - Can log data to a file
 - Customizable colours
 - Displays data in different formats: ASCII, BIN, OCT or DEC
 - Can open multiple instances

## Important

Depending on your system, you may need to add a user to the dialout group to open serial ports:

```bash
sudo usermod -a -G dialout $USER
sudo usermod -a -G plugdev $USER
```

You may also need to install udev rules. PlatformIO have a good [instructions](https://docs.platformio.org/en/latest/core/installation/udev-rules.html)

## Screenshots

![Light mode](data/screenshots/light.png)

![Dark mode](data/screenshots/dark.png)

![Preferences window](data/screenshots/pref.png)

![Log file](data/screenshots/log.png)

## Install

### Flatpak

[![Get it from the Flathub](https://dl.flathub.org/assets/badges/flathub-badge-en.png)](https://flathub.org/apps/art.taunoerik.tauno-monitor)

### Snap

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/tauno-monitor)

Ubuntu users also must enable "Access USB hardware directly" on the Ubuntu Software Store:

![Ubuntu permissions](data/screenshots/ubuntu_access_usb_directly.png)

Or from the command line:

```bash
snap connect tauno-monitor:raw-usb
```

## Build

You can build Tauno Monitor using [GNOME Builder](https://flathub.org/et/apps/org.gnome.Builder): import the project and press the Play button.

## Support

<a href="https://www.buymeacoffee.com/taunoerik" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

 ___

Copyright 2023-2025 Tauno Erik https://taunoerik.art
