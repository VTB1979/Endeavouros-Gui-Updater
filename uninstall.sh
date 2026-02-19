#!/bin/bash
set -e

sudo rm -f /usr/bin/endeavouros-updater
sudo rm -f /usr/bin/endeavouros-pacman-update
sudo rm -f /usr/share/applications/endeavouros-updater.desktop
sudo rm -f /usr/share/polkit-1/actions/de.endeavouros.updater.policy
sudo rm -f /usr/share/icons/hicolor/256x256/apps/endeavouros-updater.png

sudo gtk-update-icon-cache -f /usr/share/icons/hicolor
