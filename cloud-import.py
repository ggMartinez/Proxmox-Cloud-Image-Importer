#!/usr/bin/python3

import signal
import argparse
import os
import requests
from simple_term_menu import TerminalMenu

def getImagesList():
    ImagesURL="https://gist.githubusercontent.com/ggMartinez/f20f83d6a7630ab49d782abfe9017bc5/raw/3fb857a37b413403322e21469e155922bbac7d0c/sources.json"
    return requests.get(ImagesURL).json()

def getStorage():
    return "local-lvm"

def getId():
    id = 20000
    output = os.popen('qm list').read()
    if str(id) in output:
        id = int(os.popen('echo $(qm list | tail -| tr -s " " | cut -d " " -f2 | tail -1)').read()) + 1
    return id

def importTemplate(name, storage, id):
    file = name.replace(" ", "")
    file = f"/tmp/{file}"
    print(f"Importing {file} to {storage} with id {id}")
    templateName = os.path.basename(file).split(".")[0]
    os.popen(f'qm create {id} --memory 2048 --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci  --name "{templateName}" | cut -d"." -f1').read()
    os.popen(f'qm set {id} --scsi0 {storage}:0,import-from={file}').read()
    os.popen(f'qm set {id} --ide2 {storage}:cloudinit').read()
    os.popen(f'qm set {id} --boot order=scsi0').read()
    os.popen(f'qm set {id} --serial0 socket --vga serial0').read()
    os.popen(f'qm template {id}').read()

def generateMenuOptions():
    ImagesList = getImagesList()
    menuOptions = []
    menuOptions.append("Download All")
    for image in ImagesList:
        menuOptions.append(image['Name'])
    return menuOptions

def downloadImage(image):
    file = image["Name"].replace(" ", "")
    if str(file) in os.popen('qm list').read():
        return False
    print(f"Downloading template '{image['Name']}'... ")
    with open(f"/tmp/{file}", 'wb') as f:
        f.write(requests.get(image["URL"]).content)
    return True

def deleteImage(file):
    file = file.replace(" ","")
    os.remove(f"/tmp/{file}")

def importAllImages():
    ImagesList = getImagesList()
    for image in ImagesList:
        downloadImage(image)
        importTemplate(image['Name'], getStorage(), getId())
        deleteImage(image['Name'])

def importImage(index):
    ImagesList = getImagesList()
    if(downloadImage(ImagesList[index])):
        importTemplate(ImagesList[index]['Name'], getStorage(), getId())
        deleteImage(ImagesList[index]['Name'])
    else:
        print(f"Template '{ImagesList[index]['Name']}' already exists")

def showMenu():
    terminalMenu = TerminalMenu(generateMenuOptions())
    menuEntryIndex = terminalMenu.show()
    if menuEntryIndex == 0:
        importAllImages()
    else:
        importImage(menuEntryIndex-1)



def signalHandler(signum,frame):
    print("Exiting...                                                          ")
    exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT,signalHandler)
    showMenu()
