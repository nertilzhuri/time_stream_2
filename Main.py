import timeimport threading
from scapy.all import *

import Stream from Stream

#Dictionary of streams (to find the stream faster)
streams = {}

DEBUG = 0; #level 0, 1, 2, 3

def manage_pckg(pack):
    """
        This handles the captured packets
        Get the TCP packets and format them to a 'stream' dictionary
        Another thread will decide if the stream IS a stream or not
    """
    if pack.haslayer("TCP"):
        ip1 = pack[IP].src
        ip2 = pack[IP].dst

        ip = str(ip1)+"|"+str(ip2)
        temp_ip = str(ip2)+"|"+str(ip1)
        blacklisted = False
        is_stream = 0

        if stream_val.has_key(ip):
            #check if it is blacklisted
            Stream s = streams[ip]
            if s.blacklisted:
                blacklisted = True
        elif stream_val.has_key(temp_ip):
            #Using the same IP's
            ip = temp_ip
            Stream s = streams[ip]
            if s.blacklisted:
                blacklisted = True
        else:
            streams(ip) = Streams(ip, DEBUG)

        if not blacklisted:

            #No timestamp no stream (decide directly)
            if not "Timestamp" in str(pack[TCP].options):
                if DEBUG > 2:
                    print("Stream "+ip+" blacklisted due to no Timestamp")
                streams[ip].blacklisted = True;
                return #end the thread here

            timestamp = ""

            #Reading the RAW data for information (HTTP)
            if pack.haslayer(Raw):
                if not "HTTP" in pack[Raw].load:
                    if DEBUG > 2:
                        print("Stream "+ip+" blacklisted due to no HTTP")
                    streams[ip].blacklisted = True;
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

                    streams[ip].record_packet(timestamp, clock_t, has_av, has_hls_content_type, has_dash_content_type)

            else:
                if DEBUG > 2:
                    print("Stream "+ip+" blacklisted due to no Raw layer")
                streams[ip].blacklisted = True;
                return #end the thread here

#call sniffer:
sniff(prn=manage_pckg, store=0)
