import os, glob, time
import shutil
import win32file, win32api


# set the destination folder where to copy the content of the usb drives
dest_dir = "Destination_directory"


def locate_usb():
    drive_list = []
    drivebits = win32file.GetLogicalDrives()
    for d in range(1, 26):
        mask = 1 << d
        if drivebits & mask:
            drname = '%c:\\' % chr(ord('A') + d)
            t = win32file.GetDriveType(drname)
            if t == win32file.DRIVE_REMOVABLE:
                drive_list.append(drname)
    return drive_list


def try_copy(file, drivename):
    try:
        d = ""
        if drivename.strip() != "":
            d = os.sep + drivename

        dir = dest_dir + d + os.sep + str(os.sep).join(file.split(os.sep)[1:len(file.split(os.sep)) - 1])

        if not os.path.isdir(dir):
            try:
                os.mkdir(dir)
            except:
                pass
        shutil.copy(file, dest_dir + d + file.split(":")[1])
        print("%s OK" % file)
    except:
        print("%s Error" % file)


def recurs_walk(item, drivename):
    if os.path.isdir(item):
        files_list = [k for k in glob.glob(item + os.sep + "*")]
        if files_list:
            for item2 in files_list:
                print(item2)
                if os.path.isdir(item2):
                    recurs_walk(item2, drivename)
                else:
                    try_copy(item2, drivename)
    else:
        try_copy(item, drivename)


init_list = []
while True:
    if not os.path.isdir(dest_dir):
        try:
            os.mkdir(dest_dir)
        except:
            break
    tmp_list = locate_usb()
    for drv in init_list:
        if drv not in tmp_list:
            print("drive %s is been removed" % drv)
            del init_list[init_list.index(drv)]

    drive_list = [k for k in tmp_list if k not in init_list]
    init_list += drive_list
    for drive in drive_list:
        try:
            drivename = win32api.GetVolumeInformation(drive)[0].replace(" ", "_")
        except:
            drivename = "unknown"
        if drivename.strip() != "":
            try:
                os.mkdir(dest_dir + os.sep + drivename)
            except:
                pass
        print("exploring %s" % drive)
        files_list = [k for k in glob.glob(drive + "*") if "System Volume Information" not in k]
        if files_list:
            for item in files_list:
                recurs_walk(item, drivename)
        else:
            print("nothing found on this drive")
            del init_list[init_list.index(drive)]

    time.sleep(5)
