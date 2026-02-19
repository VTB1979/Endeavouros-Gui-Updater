#!/bin/bash
set -e

sudo install -Dm755 updater.py /usr/bin/endeavouros-updater
sudo install -Dm755 pacman-update.sh /usr/bin/endeavouros-pacman-update
sudo install -Dm644 endeavouros-updater.desktop /usr/share/applications/endeavouros-updater.desktop
sudo install -Dm644 endeavouros-updater.policy /usr/share/polkit-1/actions/de.endeavouros.updater.policy
sudo install -Dm644 endeavouros-updater.png /usr/share/icons/hicolor/256x256/apps/endeavouros-updater.png

sudo gtk-update-icon-cache -f /usr/share/icons/hicolor
