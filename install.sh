#!/bin/bash

currentDirectory=$(pwd)
outputDirectory="/opt/Proxmox-Cloud-Image-Importer"

echo "Installing Python Pip" 
sudo apt-get install python3-pip

echo "Installing requirements"
pip3 install -r requirements.txt

echo "Downloading importer"
git clone https://github.com/ggMartinez/Proxmox-Cloud-Image-Importer $outputDirectory && cd $outputDirectory

echo "Creating symlink"
ln -s $outputDirectory/cloud-import.py /usr/bin/cloud-import 


echo "Installed!! Run with 'cloud-import'"
echo "If you want to update, run \"cd $outputDirectory && git pull\"."

cd $currentDirectory