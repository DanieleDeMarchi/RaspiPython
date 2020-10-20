#!/usr/bin/env python3

# Copyright (c) 2009, Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
List all mounted disk partitions a-la "df -h" command.
$ python3 scripts/disk.py
Device               Total     Used     Free  Use %      Type  Mount
C:\                 232.3G    75.3G   157.0G    32%      NTFS  C:\
D:\                 476.8G   341.6G   135.2G    71%      NTFS  D:\
G:\                 465.8G   390.8G    74.9G    83%      NTFS  G:\
H:\                 512.0G   350.3G   161.7G    68%      NTFS  H:\
"""

import sys
import os
import psutil
import copy
from psutil._common import bytes2human

class HardDrive:
    def getHarDriveUsage():
        disk_usage = []
        for partition in psutil.disk_partitions(all=False):
            if "cdrom" in partition.opts or partition.fstype == "":
                # skip cd-rom drives with no disk in it; they may raise
                # ENOENT, pop-up a Windows GUI error for a non-ready
                # partition or just hang.
                continue
            usage = psutil.disk_usage(partition.mountpoint)
            partition = {"partitionName": partition.device,
                         "total" : int(usage.total/1024**2),
                         "free" : int(usage.free/1024**2),
                         "type" : partition.fstype
                        }
            disk_usage.append(copy.deepcopy(partition))
        return disk_usage

def main():
    templ = "%-17s %8s %8s %8s %5s%% %9s  %s"
    print(templ % ("Device", "Total", "Used", "Free", "Use ", "Type", "Mount"))
    for part in psutil.disk_partitions(all=False):
        if os.name == "nt":
            if "cdrom" in part.opts or part.fstype == "":
                # skip cd-rom drives with no disk in it; they may raise
                # ENOENT, pop-up a Windows GUI error for a non-ready
                # partition or just hang.
                continue
        usage = psutil.disk_usage(part.mountpoint)
        print(
            templ
            % (
                part.device,
                bytes2human(usage.total),
                bytes2human(usage.used),
                bytes2human(usage.free),
                int(usage.percent),
                part.fstype,
                part.mountpoint,
            )
        )

    print(HardDrive.getHarDriveUsage())


if __name__ == "__main__":
    sys.exit(main())
