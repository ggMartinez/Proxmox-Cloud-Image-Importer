#!/bin/bash

set -e

# Detectar versión principal de Proxmox (7, 8 o 9)
proxmoxVersion=$(pveversion --verbose | grep proxmox-ve | awk '{print $2}' | cut -d"." -f1)
currentDirectory=$(pwd)
outputDirectory="/opt/Proxmox-Cloud-Image-Importer"
binaryLink="/usr/local/bin/cloud-import"

echo
echo "=== Proxmox Cloud Image Importer Installer ==="
echo

# Verificar e instalar Git
if ! command -v git >/dev/null 2>&1; then
    echo "🔧 Installing Git..."
    apt-get update && apt-get install git -y
else
    echo "✅ Git is already installed. Skipping..."
fi

# Verificar e instalar pip3
if ! command -v pip3 >/dev/null 2>&1; then
    echo "🔧 Installing Python3 pip..."
    apt-get install python3-pip -y
else
    echo "✅ Python3 pip is already installed. Skipping..."
fi

echo
echo "📥 Downloading importer from GitHub..."
if [ -d "$outputDirectory" ]; then
    echo "⚠️  Directory $outputDirectory already exists. Pulling latest changes..."
    cd "$outputDirectory" && git pull
else
    git clone https://github.com/ggMartinez/Proxmox-Cloud-Image-Importer "$outputDirectory"
    cd "$outputDirectory" && git config core.fileMode false
fi

echo
echo "📦 Installing Python requirements..."
cd "$outputDirectory"
if [ "$proxmoxVersion" = "7" ]; then
    python3 -m pip install -r requirements.txt
elif [ "$proxmoxVersion" = "8" ] || [ "$proxmoxVersion" = "9" ]; then
    python3 -m pip install -r requirements.txt --break-system-packages
else
    echo "❌ Unsupported Proxmox version: $proxmoxVersion"
    exit 1
fi

echo
echo "🔗 Creating symlink in /usr/local/bin..."
if [ -L "$binaryLink" ]; then
    echo "ℹ️  Symlink already exists. Skipping..."
else
    ln -s "$outputDirectory/cloud-import.py" "$binaryLink"
    chmod +x "$outputDirectory/cloud-import.py"
    echo "✅ Symlink created at $binaryLink"
fi

echo
echo "✅ Installed successfully!"
echo "➡️  Run with: cloud-import"
echo "➡️  To update in the future: cd $outputDirectory && git pull"
echo

cd "$currentDirectory"

