#!/bin/bash

# Path changes between Raspberry Pi OS versions
if grep -qi "bullseye" /etc/os-release; then
    CFG="/boot/config.txt"
else
    CFG="/boot/firmware/config.txt"
fi

echo "Using config file: $CFG"

# Backup
sudo cp "$CFG" "${CFG}.bak_$(date +%Y%m%d%H%M%S)"

# Change camera_auto_detect value from 1 to 0
echo "Updating camera_auto_detect..."
if grep -q '^camera_auto_detect=1' "$CFG"; then
    sudo sed -i 's/^camera_auto_detect=1$/camera_auto_detect=0/' "$CFG"
elif grep -q '^camera_auto_detect=0' "$CFG"; then
    echo "camera_auto_detect is already set to 0"
else
    echo "ERROR: camera_auto_detect not found in $CFG"
    exit 1
fi

echo "Ensuring dtoverlay=imx708 under [all]..."
if ! grep -q '^dtoverlay=imx708' "$CFG"; then
    if grep -q '^\[all\]' "$CFG"; then
        sudo sed -i '/^\[all\]/a dtoverlay=imx708' "$CFG"
    else
        echo "ERROR: [all] not found IN $CFG"
        exit 1
    fi
else
    echo "dtoverlay=imx708 already present."
fi

echo "Done!"
