import time
import threading
import datetime
from scapy.all import *
from Stream import *

#Dictionary of streams (to find the stream faster)
streams = {}

DEBUG = 1; #level 0, 1, 2, 3

plot_file = "time-2.txt"

def sync():
    """
        This thread will collect the calculated times and display
        Here the marzullos algorithm can be implemented for security increase
    """

    while True:
        for k in streams.keys():
            if streams[k].isSynchronizer:
                f = open(plot_file, 'a')
                calc_hour = streams[k].synced_hour
                sys_hour = str(datetime.datetime.now().strftime('%H:%M:%S'))
                #min_pack = streams[k].minimum_num_to_sync

                #avg_delay = streams[k].average_delay;

                #print "Calculated Time: "+str(calc_hour)+" delay: "+str(avg_delay)
                #print "System Time: "+str(sys_hour)
                #print "Minimum Number of packets to synchronize: "+str(min_pack)
                f.write(""+str(sys_hour)+","+str(calc_hour)+"\n")
                f.close()
                time.sleep(0.5)

def manage_pckg(pack):
    """
        This handles the captured packets
        Get the TCP packets and format them to a 'stream' dictionary
        Another thread will decide if the stream IS a stream or not
    """
    if pack.haslayer("TCP"):
        ip1 = pack[IP].src
        ip2 = pack[IP].dst

        src = ip1

        ip = str(ip1)+"|"+str(ip2)
        temp_ip = str(ip2)+"|"+str(ip1)
        blacklisted = False
        is_stream = 0

        if streams.has_key(ip):
            #check if it is blacklisted
            s = streams[ip]
            if s.blacklisted:
                blacklisted = True
        elif streams.has_key(temp_ip):
            #Using the same IP's
            ip = temp_ip
            s = streams[ip]
            if s.blacklisted:
                blacklisted = True
        else:
            streams[ip] = Stream(ip, DEBUG)

        if not blacklisted:

            #No timestamp no stream (decide directly)
            if not "Timestamp" in str(pack[TCP].options):
                if DEBUG >= 2:
                    print("Stream "+ip+" blacklisted due to no Timestamp")
                streams[ip].blacklist()
                return #end the thread here

            ss = str(pack[TCP].options)
            i1=ss.find("(", ss.find("Timestamp"))
            i2=ss.find(")", i1)
            timestamp = ss[i1+1:i2].split(",")

            #Reading the RAW data for information (HTTP)
            if pack.haslayer(Raw):
                if not "HTTP" in pack[Raw].load:
                    #if DEBUG >= 2:
                        #print("Stream "+ip+" blacklisted due to no HTTP")
                    #streams[ip].blacklisted = True;
                    return #end the thread here
                else:
                    #there is HTTP, extract information
                    payload = pack[Raw].load

                    clock_t = []

                    #Date cannot blacklist since only server sends time
                    if "Date" in payload:
                        #Extracting time:
                        s = payload

                        s = s.replace("\r", "|")
                        s = s.replace("\n", "|")
                        s = s.replace(":", "|")

                        t = s.split("|")

                        clock_t = (str(t[t.index('Date')+1])+" "+str(t[t.index('Date')+2])+" "+str(t[t.index('Date')+3])).strip().rstrip().replace(",", "").split(" ")

                    #This is taken from client requests
                    has_av = (("-audio" in payload) and ("-video" in payload))

                    #this is taken from server stream
                    has_hls_content_type = "Content-Type: application/vnd.apple.mpegurl" in payload or "Content-Type: application/x-mpegURL" in payload
                    has_dash_content_type = "Content-Type: application/octet-stream" in payload

                    streams[ip].record_packet(timestamp, clock_t, has_av, has_hls_content_type, has_dash_content_type, src)

            else:
                #if DEBUG >= 2:
                #    print("Stream "+ip+" blacklisted due to no Raw layer")
                #streams[ip].blacklisted = True;
                return #end the thread here

threading.Thread(target=sync).start()

#call sniffer:
sniff(prn=manage_pckg, store=0)
