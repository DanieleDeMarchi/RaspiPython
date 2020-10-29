import time
import sys
import os
import psutil
import copy
from datetime import datetime, timezone, timedelta

"""[summary]

    Classe per misurazione attività della rete.
    Per ogni scheda di rete ritorna un dizionario nel seguente formato
    net_data = {"interface_name": None, "kbps_sent": None, "kbps_recv": None}

"""

net_data = {"interface_name": None, "kbps_sent": None, "kbps_recv": None}


def getPcTime():
    diff = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0)
    timestampPc = diff.days * 24 * 60 * 60 + diff.seconds + diff.microseconds * (10 ** (-6))
    return timestampPc

class NetMeasurement:
    def __init__(self):
        self.pnic_before = psutil.net_io_counters(pernic=True)
        self.old_timestamp = getPcTime()

    def newMeasurement(self):
        new_pnic = psutil.net_io_counters(pernic=True)
        timestamp = getPcTime()
        time_delta = timestamp - self.old_timestamp
        self.old_timestamp = timestamp

        nic_names = list(new_pnic.keys())
        diff_nic = []
        for name in nic_names:
            if new_pnic[name].bytes_sent > 0 or new_pnic[name].bytes_recv > 0:
                if name in self.pnic_before:
                    sent_per_sec = (
                        (new_pnic[name].bytes_sent - self.pnic_before[name].bytes_sent)
                        / 1024
                        * 8
                        / time_delta
                    )
                    recv_per_sec = (
                        (new_pnic[name].bytes_recv - self.pnic_before[name].bytes_recv)
                        / 1024
                        * 8
                        / time_delta
                    )
                    diff_nic.append(
                        {
                            "name": name,
                            "sent_per_sec": int(sent_per_sec),
                            "recv_per_sec": int(recv_per_sec),
                        }
                    )

        self.pnic_before = new_pnic
        return diff_nic

    def getData(self):
        update = self.newMeasurement()

        netdata_array = []

        for nic in update:
            net_data["interface_name"] = nic["name"]
            net_data["kbps_sent"] = nic["sent_per_sec"]
            net_data["kbps_recv"] = nic["recv_per_sec"]
            netdata_array.append(copy.deepcopy(net_data))
        return netdata_array


def main():
    netstat = NetMeasurement()
    print(getPcTime())
    while True:
        #os.system("cls")
        newmes = netstat.newMeasurement()
        for mes in newmes:
            print(
                "Nome scheda di rete: {}\t upload: {} kbps\t download: {} kbps".format(
                    mes["name"], mes["sent_per_sec"], mes["recv_per_sec"]
                )
            )
        time.sleep(3)


if __name__ == "__main__":
    main()
