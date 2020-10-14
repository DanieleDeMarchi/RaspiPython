
from __future__ import print_function
import collections
import os
import sys
import time

import psutil
from psutil._compat import get_terminal_size
import os


def main():
    os.system('cls')
    num_cpus = psutil.cpu_count()
    if num_cpus > 8:
        num_cpus = 8  # try to fit into screen
        cpus_hidden = True
    else:
        cpus_hidden = False

    for i in range(num_cpus):
        print("Core %-5i" % i, end="")
    print("CPU       ", end="")
    print("Frequenza ", end="")
    if cpus_hidden:
        print(" (+ hidden)", end="")
    print()

    while True:
        # header
        cpus_percent = psutil.cpu_percent(percpu=True)
        media_cpu = psutil.cpu_percent(percpu=False)
        for _ in range(num_cpus):
            print("%-10s" % cpus_percent.pop(0), end="")
        print("%-10s" % media_cpu, end="")
        print("%-6s MHz" % psutil.cpu_freq().current, end="")
        print(end="\r", flush=True)

        time.sleep(0.5)


if __name__ == '__main__':
    main()
