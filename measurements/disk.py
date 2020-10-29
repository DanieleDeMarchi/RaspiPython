import json
import sys
import os
import psutil
import copy
from psutil._common import bytes2human

"""[summary]

    Classe per misurazione spazio disponibile su disco.

"""

class HardDrive:
    def getHarDriveUsage():
        disk_usage = []
        for partition in psutil.disk_partitions(all=False):
            if "cdrom" in partition.opts or partition.fstype == "":
                # skip cd-rom
                continue
            usage = psutil.disk_usage(partition.mountpoint)
            partition = {"partitionName": partition.device,
                         "total" : int(usage.total/1024**2),
                         "free" : int(usage.free/1024**2),
                         "type" : partition.fstype
                        }
            disk_usage.append(copy.deepcopy(partition))
        return disk_usage

    def getHardDriveUsageString():
        templ = "%-6s %6s %6s %4s%% %6s \n"
        string = (templ % ("Device", "Total", "Free", "Use", "Type"))
        for part in psutil.disk_partitions(all=False):
            if os.name == "nt":
                if "cdrom" in part.opts or part.fstype == "":
                    # skip cd-rom drives 
                    continue
            usage = psutil.disk_usage(part.mountpoint)
            string+=(
                templ
                % (
                    part.device,
                    bytes2human(usage.total),
                    bytes2human(usage.free),
                    int(usage.percent),
                    part.fstype,
                )
            )
        
        return string


def main():
    
    print(HardDrive.getHardDriveUsageString())
    print(HardDrive.getHarDriveUsage())


if __name__ == "__main__":
    sys.exit(main())
