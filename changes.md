# changes.md
## CLI (`cloud-import.py`)

* Añadida interfaz de argumentos (`argparse`): `--vmid`, `--cpu`, `--memory`, `--bridge`, `--storage`, `--output-dir`, `--keep`, `--list`, `--import`.
* Descargas en streaming con barra de progreso (`tqdm`) y verificación de tamaño mínimo.
* Selección flexible de imágenes: por índice, nombre, nombre sin espacios o `all`; opción de listado rápido (`--list`).
* `getNextId` más robusto (ordena numéricamente e ignora encabezado).
* Flujo de importación actualizado: `qm importdisk` → `scsi0`; CPU/memoria/bridge parametrizables.
* Cloud-Init por defecto (`ciuser/cipassword=cloud`, DHCP).
* Idempotencia de descarga: evita volver a descargar si el archivo ya existe; manejo de extensiones de URL.
* Mensajes de estado más claros y limpieza general.

## Instalador (`install.sh`)

* Soporte para Proxmox 7/8/9; uso de `--break-system-packages` en 8/9.
* Uso de `python3 -m pip` y `apt-get update` al instalar dependencias.
* Variables y mensajes más claros; `set -e` para fail-fast.
