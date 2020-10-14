#!/usr/bin/env python3
#
# $Id: iotop.py 1160 2011-10-14 18:50:36Z g.rodola@gmail.com $
#
# Copyright (c) 2009, Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
Shows real-time network statistics.
Author: Giampaolo Rodola' <g.rodola@gmail.com>
$ python3 scripts/nettop.py
-----------------------------------------------------------
total bytes:           sent: 1.49 G       received: 4.82 G
total packets:         sent: 7338724      received: 8082712
wlan0                     TOTAL         PER-SEC
-----------------------------------------------------------
bytes-sent               1.29 G        0.00 B/s
bytes-recv               3.48 G        0.00 B/s
pkts-sent               7221782               0
pkts-recv               6753724               0
eth1                      TOTAL         PER-SEC
-----------------------------------------------------------
bytes-sent             131.77 M        0.00 B/s
bytes-recv               1.28 G        0.00 B/s
pkts-sent                     0               0
pkts-recv               1214470               0
"""

import time
import sys
import psutil
from psutil._common import bytes2human


def poll(interval):
    """Retrieve raw stats within an interval window."""
    tot_before = psutil.net_io_counters()
    pnic_before = psutil.net_io_counters(pernic=True)
    # sleep some time
    time.sleep(interval)
    tot_after = psutil.net_io_counters()
    pnic_after = psutil.net_io_counters(pernic=True)
    return (tot_before, tot_after, pnic_before, pnic_after)


def refresh_window(tot_before, tot_after, pnic_before, pnic_after):
    """Print stats on screen."""
    global lineno

    # totals
    print("total bytes:     sent: %-6s   received: %s" % (
        bytes2human(tot_after.bytes_sent),
        bytes2human(tot_after.bytes_recv))
    )
    print("total packets:   sent: %-6s   received: %s" % (
        tot_after.packets_sent, tot_after.packets_recv))

    # per-network interface details: let's sort network interfaces so
    # that the ones which generated more traffic are shown first
    nic_names = list(pnic_after.keys())
    nic_names.sort(key=lambda x: sum(pnic_after[x]), reverse=True)
    for name in nic_names:
        stats_before = pnic_before[name]
        stats_after = pnic_after[name]
        templ = "%-15s %15s %15s"
        print(name + " TOTAL" + " PER-SEC")
        print("bytes-sent: " +
              bytes2human(stats_after.bytes_sent) + " " +
              bytes2human(stats_after.bytes_sent -
                          stats_before.bytes_sent) + '/s',
              )
        print("bytes-recv: " +
              bytes2human(stats_after.bytes_recv) + " " +
              bytes2human(
                  stats_after.bytes_recv - stats_before.bytes_recv) + '/s',
              )


def main():
    args = poll(1)
    refresh_window(*args)


if __name__ == '__main__':
    main()
