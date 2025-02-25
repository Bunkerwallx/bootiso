import os
import subprocess
from tkinter import Tk, Label, Button, filedialog, messagebox

def list_usb_devices():
    devices = []
    try:
        output = subprocess.check_output("lsblk -lp | grep 'part $' | grep -v 'rom' | awk '{print $1}'", shell=True)
        devices = output.decode().strip().split('\n')
    except subprocess.CalledProcessError:
        pass
    return devices

def select_iso():
    iso_path = filedialog.askopenfilename(filetypes=[("ISO files", "*.iso")])
    return iso_path

def partition_usb(device):
    try:
        commands = [
            f"parted {device} mklabel gpt",
            f"parted {device} mkpart primary fat32 1MiB 100MiB",
            f"parted {device} mkpart primary ext4 100MiB 50%",
            f"parted {device} mkpart primary ext4 50% 100%",
            f"mkfs.fat -F32 {device}1",
        ]
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True)
        messagebox.showinfo("Success", "Partitioning completed!")
    except Exception as e:
        messagebox.showerror("Error", f"Partitioning failed: {e}")

def write_iso_to_partition(iso_path, partition):
    try:
        subprocess.run(f"sudo dd if={iso_path} of={partition} bs=4M status=progress", shell=True, check=True)
        messagebox.showinfo("Success", f"ISO written to {partition}!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write ISO: {e}")

def setup_grub(device):
    try:
        commands = [
            f"mount {device}1 /mnt",
            "grub-install --target=x86_64-efi --efi-directory=/mnt --boot-directory=/mnt/boot --removable",
            "umount /mnt",
        ]
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True)
        messagebox.showinfo("Success", "GRUB installed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to install GRUB: {e}")

def main():
    root = Tk()
    root.title("USB Multiboot Creator")

    Label(root, text="1. Select USB Device:").pack()
    usb_list = list_usb_devices()
    if not usb_list:
        messagebox.showerror("Error", "No USB devices found!")
        root.quit()
    usb_var = usb_list[0]

    Button(root, text="Partition USB", command=lambda: partition_usb(usb_var)).pack()

    Label(root, text="2. Select ISO File:").pack()
    iso_path = Button(root, text="Browse ISO", command=select_iso).pack()

    Label(root, text="3. Write ISO to USB Partition:").pack()
    Button(root, text="Write ISO", command=lambda: write_iso_to_partition(iso_path, usb_var)).pack()

    Label(root, text="4. Install GRUB:").pack()
    Button(root, text="Install GRUB", command=lambda: setup_grub(usb_var)).pack()

    root.mainloop()

if __name__ == "__main__":
    main()
