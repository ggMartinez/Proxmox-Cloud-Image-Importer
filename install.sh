#!/bin/bash

set -e

proxmoxVersion=$(pveversion --verbose| grep proxmox-ve| cut -d" " -f2| cut -d"." -f1 )
currentDirectory=$(pwd)
outputDirectory="/opt/Proxmox-Cloud-Image-Importer"

if ! [ -x "$(command -v git)" ]; then
    echo "Installing Git... \n\n"
    sudo apt-get install git -y
else
    echo "Git is already installed. Skipping... \n\n"
fi


if ! [ -x "$(command -v pip3)" ]; then
    echo "Installing Python3 Pip... \n\n"
    sudo apt-get install python3-pip -y
else
    echo "Python3 Pip is already installed. Skipping... \n\n"
fi

echo "Downloading importer... \n\n"
git clone https://github.com/ggMartinez/Proxmox-Cloud-Image-Importer $outputDirectory && cd $outputDirectory


echo "Installing requirements\n\n"
if [  "$proxmoxVersion" = "7" ]
then
    pip3 install -r requirements.txt
fi
if [ "$proxmoxVersion" = "8" ]
then
    pip3 install -r requirements.txt  --break-system-packages
fi


echo "Creating symlink in /usr/local/bin/cloud-import... \n\n"
ln -s $outputDirectory/cloud-import.py /usr/bin/local/cloud-import && chmod +x $outputDirectory/cloud-import.py


echo "Installed!! Run with 'cloud-import' \n"
echo "If you want to update, run \"cd $outputDirectory && git pull\".\n\n"

cd $currentDirectory