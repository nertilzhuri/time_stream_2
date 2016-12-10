import time
import threading
from scapy.all import *
import math

my_src = "192.168.0.110"
dest1 = "178.79.196.254"
dest2 = "178.79.196.253"

segments = []
loads = []
delays = []

curr_seg = 0
curr_load = 0

pack_cnt = 0
pack_print = 200

dd = 0

def manage_pckg(pack):
    global delays, dd, pack_cnt, pack_print, segments, loads, curr_seg, curr_load

    if pack.haslayer("TCP"):
        src = pack[IP].src
        dest = pack[IP].dst

        #print("SRC: "+src+" DEST: "+dest)
        if src == dest1 or src == dest2:
            curr_seg += 1
            curr_load += len(pack)

            if dd == 0:
                dd = time.time() #get first time

        elif src == my_src:
            if curr_seg > 0:
                segments.append(curr_seg)
                loads.append(curr_load)
                curr_seg = 0
                curr_load = 0

                delays.append(time.time() - dd)
                dd = 0
                #print(delays[-1])

        pack_cnt += 1

        if pack_cnt % pack_print == 0:
            delays = delays[20:]
            ss = sum(delays)
            size = len(delays)
            avg = float(ss)/float(size)
            mm = max(delays)
            print("S: "+str(ss)+" L: "+str(size)+" M: "+str(mm)+" A: "+str(avg))

#call sniffer:
sniff(prn=manage_pckg, store=0)
