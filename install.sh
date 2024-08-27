#!/bin/bash

set -e

currentDirectory=$(pwd)
outputDirectory="/opt/Proxmox-Cloud-Image-Importer"

if ! [ -x "$(command -v git)" ]; then
    echo "Installing Git..." 
    sudo apt-get install git -y
else 
    echo "Git is already installed. Skipping... "
fi


if ! [ -x "$(command -v pip3)" ]; then
    echo "Installing Python3 Pip..." 
    sudo apt-get install python3-pip -y
else 
    echo "Python3 Pip is already installed. Skipping... "
fi

echo "Downloading importer"
git clone https://github.com/ggMartinez/Proxmox-Cloud-Image-Importer $outputDirectory && cd $outputDirectory


echo "Installing requirements"
pip3 install -r requirements.txt


echo "Creating symlink"
ln -s $outputDirectory/cloud-import.py /usr/bin/cloud-import 


echo "Installed!! Run with 'cloud-import'"
echo "If you want to update, run \"cd $outputDirectory && git pull\"."

cd $currentDirectory