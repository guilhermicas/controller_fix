#!/usr/bin/env python3

import subprocess
import os
import sys

"""
The purpose of this script is to make my third party crappy controller work

1.
It deletes orphan joystick char devices on /dev/input/, because sometimes they get 'stuck'

2.
Then it restarts the xboxdrv service to recreate the joystick char devices

3.
Then it probes the controller with certain values to initialize it
"""


def delete_diff_js():
    # 1. Getting Joystick Devices from /dev/input

    # ls /dev/input/
    find_js_proc = subprocess.Popen(
        ("ls", "/dev/input/"), stdout=subprocess.PIPE)

    # grab previous command output and do "| grep js" to get only joystick devices
    js_list = subprocess.check_output(
        ("grep", "js"), stdin=find_js_proc.stdout)

    # formatting list properly
    js_list = js_list.decode().split("\n")[:-1]

    # 2. Iterate through list, if device is not a Mouse, then delete it

    for jsX in js_list:
        p = subprocess.Popen(
            ["jstest", "--normal", f"/dev/input/{jsX}"], stdout=subprocess.PIPE)

        # redundant readline, retrieves driver version
        p.stdout.readline()

        # Gets the device name
        js_name = p.stdout.readline().decode()

        # Killing jstest because there isnt a way to just check the dev name, maybe there is im noob at linux devices
        p.kill()

        # If device is not mouse, delete it
        # TODO: there should be a better way to do this, identify which of the js devices is controller specifically
        if("Mouse" not in js_name):
            #print("IS NOT MOUSE")
            os.system(f"rm -rf /dev/input/{jsX}")
            # print(js_name)


try:
    import usb.core
    import usb.util
except ImportError:
    print("First, install the pyusb module with PIP or your package manager.")
else:
    if os.geteuid() != 0:
        print("You need to run this script with sudo")
        sys.exit()

    # 1. Deleting broken js devices
    delete_diff_js()

    # 2. Restart xboxdrv.service
    os.system("sudo systemctl restart xboxdrv.service")

    # 3. Probe Controller

    dev = usb.core.find(find_all=True)

    for d in dev:
        if d.idVendor == 0x045e and d.idProduct == 0x028e:
            d.ctrl_transfer(0xc1, 0x01, 0x0100, 0x00, 0x14)
finally:
    sys.exit()
