# Proxmox - Cloud Image Importer

 
## Requirements 
This script requires `python3-pip`, `git`, and the Python Package [Simpe term menu](https://pypi.org/project/simple-term-menu/). 

But if you don't have them, the install script will install them for you.

Tested on Proxmox 7.X and Proxmox 8.X.
## Install 

Log in to a Proxmox Server via SSH, and then run: 
```bash
curl 'https://raw.githubusercontent.com/ggMartinez/Proxmox-Cloud-Image-Importer/main/install.sh' | bash
```

And then run `cloud-import`
 
 Otherwise, clone this repo where you want, make sure you have all the requirements met, and then run inside the repo directory `python3 cloud-import.py`.

## Usage

When you run the tool, you will see something like this:

![enter image description here](https://i.ibb.co/sgn3FgL/Screenshot-2024-08-27-at-2-37-49-PM.png)

Then you select the option that you want, or download all. 

The selection will download the cloud image, and then the image will be imported, and ready on your Proxmox UI, ready to clone as template. 

## Sources
Right now, the sources is just a plain JSON on a [Gist](https://gist.githubusercontent.com/ggMartinez/f20f83d6a7630ab49d782abfe9017bc5/raw/3fb857a37b413403322e21469e155922bbac7d0c/sources.json) on my account. 

I'll try to add more images. I'm open to better ways to handle this.