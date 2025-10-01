#!/usr/bin/python3

import signal
import argparse
import os
import subprocess
import requests
from urllib.parse import urlparse
from simple_term_menu import TerminalMenu
from tqdm import tqdm

def getImagesList():
    ImagesURL = "https://gist.githubusercontent.com/ggMartinez/f20f83d6a7630ab49d782abfe9017bc5/raw/sources.json"
    return requests.get(ImagesURL).json()

def getNextId(start=20000):
    output = os.popen('qm list').read()
    if str(start) in output:
        id = int(os.popen('echo $(qm list | tail -n +2 | tr -s " " | cut -d " " -f2 | sort -n | tail -1)').read()) + 1
        return id
    return start

def importTemplate(name, storage, vmid, cpu, memory, bridge, file_path):
    filename = os.path.basename(file_path)
    print(f"\n🛠️  Importing {file_path} to storage '{storage}' with VM ID {vmid}")
    vm_name = os.path.splitext(filename)[0]
    os.system(f'qm create {vmid} --memory {memory} --cores {cpu} '
              f'--net0 virtio,bridge={bridge} --scsihw virtio-scsi-pci '
              f'--name "{vm_name}"')
    os.system(f'qm importdisk {vmid} {file_path} {storage} --format qcow2')
    os.system(f'qm set {vmid} --scsi0 {storage}:vm-{vmid}-disk-0')
    os.system(f'qm set {vmid} --ide2 {storage}:cloudinit')
    os.system(f'qm set {vmid} --ciuser cloud --cipassword cloud --ipconfig0 ip=dhcp')
    os.system(f'qm set {vmid} --boot order=scsi0')
    os.system(f'qm set {vmid} --serial0 socket --vga serial0')
    os.system(f'qm template {vmid}')

def generateMenuOptions():
    images = getImagesList()
    return ["Download All"] + [img['Name'] for img in images]

def _url_ext(url):
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext if ext else ""

def _candidate_paths(base, url_ext, output_dir, keep):
    if keep:
        return [os.path.join(output_dir, base + url_ext)]
    return [os.path.join(output_dir, base), os.path.join(output_dir, base + url_ext)]

def downloadImage(image, output_dir, keep=False):
    base = image["Name"].replace(" ", "")
    ext = _url_ext(image["URL"])
    candidates = _candidate_paths(base, ext, output_dir, keep)
    for p in candidates:
        if os.path.exists(p):
            print(f"⚠️  Image '{os.path.basename(p)}' already downloaded. Skipping download.")
            return p
    filename = os.path.basename(candidates[0])
    full_path = candidates[0]
    print(f"⬇️  Downloading template '{image['Name']}'...")
    response = requests.get(image["URL"], stream=True)
    if response.status_code != 200:
        print(f"❌ Failed to download image from {image['URL']} (status: {response.status_code})")
        return None
    os.makedirs(output_dir, exist_ok=True)
    total_size = int(response.headers.get('content-length', 0))
    with open(full_path, 'wb') as f, tqdm(
        total=total_size,
        unit='B',
        unit_scale=True,
        desc=filename,
        ncols=100
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))
    size_bytes = os.path.getsize(full_path)
    size_mb = size_bytes / (1024 * 1024)
    if size_mb < 10:
        print(f"❌ Image '{filename}' is too small ({size_mb:.2f} MB). Probably an error.")
        os.remove(full_path)
        return None
    print(f"✅ Downloaded '{filename}' ({size_mb:.2f} MB)")
    return full_path

def deleteFile(path):
    if path and os.path.exists(path):
        os.remove(path)

def importAllImages(args):
    images = getImagesList()
    for image in images:
        file_path = downloadImage(image, args.output_dir, keep=args.keep)
        if file_path:
            vmid = args.vmid if args.vmid else getNextId()
            importTemplate(image['Name'], args.storage, vmid, args.cpu, args.memory, args.bridge, file_path)
            if not args.keep:
                deleteFile(file_path)

def importImageByIndex(index, args):
    images = getImagesList()
    image = images[index]
    file_path = downloadImage(image, args.output_dir, keep=args.keep)
    if file_path:
        vmid = args.vmid if args.vmid else getNextId()
        importTemplate(image['Name'], args.storage, vmid, args.cpu, args.memory, args.bridge, file_path)
        if not args.keep:
            deleteFile(file_path)
    else:
        print(f"✅ Template '{image['Name']}' already exists or was skipped.")

def showMenu(args):
    menu = TerminalMenu(generateMenuOptions())
    choice = menu.show()
    if choice == 0:
        importAllImages(args)
    else:
        importImageByIndex(choice - 1, args)

def signalHandler(signum, frame):
    print("Exiting...")
    exit(1)

def listImages():
    images = getImagesList()
    for i, img in enumerate(images, start=1):
        print(f"{i}. {img['Name']}")

def _resolve_selections(selections, images):
    indexes = set()
    names_map = {img['Name'].strip().lower(): idx for idx, img in enumerate(images)}
    for sel in selections:
        if sel.lower() in ("all", "*"):
            return list(range(len(images)))
        if sel.isdigit():
            idx = int(sel) - 1
            if 0 <= idx < len(images):
                indexes.add(idx)
        else:
            key = sel.strip().lower()
            if key in names_map:
                indexes.add(names_map[key])
            else:
                for idx, img in enumerate(images):
                    if key == img['Name'].replace(" ", "").lower():
                        indexes.add(idx)
                        break
    return sorted(indexes)

def importSelections(selections, args):
    images = getImagesList()
    idxs = _resolve_selections(selections, images)
    if not idxs:
        print("No matching images.")
        return
    for idx in idxs:
        image = images[idx]
        file_path = downloadImage(image, args.output_dir, keep=args.keep)
        if file_path:
            vmid = args.vmid if args.vmid else getNextId()
            importTemplate(image['Name'], args.storage, vmid, args.cpu, args.memory, args.bridge, file_path)
            if not args.keep:
                deleteFile(file_path)

def parseArgs():
    parser = argparse.ArgumentParser(description="Importador de plantillas cloud para Proxmox.")
    parser.add_argument("--vmid", type=int, help="ID específico para la VM (si no se indica, se genera automáticamente)")
    parser.add_argument("--cpu", type=int, default=1, help="Cantidad de CPUs (por defecto: 1)")
    parser.add_argument("--memory", type=int, default=512, help="Memoria en MB (por defecto: 512)")
    parser.add_argument("--bridge", type=str, default="vmbr0", help="Bridge de red (por defecto: vmbr0)")
    parser.add_argument("--storage", type=str, default="local-lvm", help="Nombre del almacenamiento en Proxmox (por defecto: local-lvm)")
    parser.add_argument("--output-dir", type=str, default="/tmp", help="Directorio donde guardar temporalmente las imágenes descargadas (por defecto: /tmp)")
    parser.add_argument("--keep", action="store_true", help="Mantener la imagen descargada con la extensión correcta")
    parser.add_argument("--list", action="store_true", help="Listar imágenes disponibles y salir")
    parser.add_argument("--import", dest="import_sel", nargs="*", help="Importar una o varias imágenes por índice, nombre, nombre-sin-espacios o 'all'")
    return parser.parse_args()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signalHandler)
    args = parseArgs()
    if args.list:
        listImages()
    elif args.import_sel and len(args.import_sel) > 0:
        importSelections(args.import_sel, args)
    else:
        showMenu(args)

