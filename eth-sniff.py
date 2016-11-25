"""
@author: Nertil Zhuri

Time Streaming

Done:
|->

TODO:
|->

Problems:
|-> Huge Lists of Streams will be created
    |-> Find a way to clean up
    |-> Just leave it and run the experiments

Updates:
|->

"""

import time
import threading
from scapy.all import *

"""
http://www.secdev.org/projects/scapy/doc/usage.html

http://www.tutorialspoint.com/python/python_dictionary.htm
"""

tcp_buffer  = [] #A list that will store the captured unfiltered packets

"""
These are the Stream dictionaries
The format in which these will be written are:

streams:
(IP-1, IP-2) -> timestamp, end_time, clock (if any), has_timestamps, is_http, get_av, content-type

stream_val:
(IP-1, IP-2) -> is_stream

(IP-1, IP-2) => Will be written as String: 192.168.0.2|77.231.42.33
    |-> Use split("|") to get the two IP's

(IP-1, IP-2) === (IP-2, IP-1)

"""
streams     = {} #Filtered packets into streams  
stream_val  = {} #The values that decide if it is a stream or not


"""
These are the constant indexes of the stored stream
These data fields will be used to determine if the captured packets belong to a stream
And will be determined to compute the time
"""

TIMESTAMP       = 0 #Time the packet is captured
END_TIME        = 1 #Will be used to calculate processing delay of the packet
CLOCK           = 2 #The Date-Time stored on HTTP (if it is enabled)
HAS_TS          = 3 #Boolean: if timestamps option is enabled
IS_HTTP         = 4 #The packet has HTTP layer
GET_AV          = 5 #If IS_HTTP: GET request has -audio and -video request (????)
CONTENT_TYPE    = 6 #If IS_HTTP: Content-Type of the packet is: application/vnd.apple.mpegurl

def printout():
    """
        DEBUGGING FUNCTION
        This thread will printout only streams from time to time
    """
    
    
    while True:
        time.sleep(10) #sleep

        for k in stream_val.keys():
            if stream_val[k] == 1:
                kk = k.split("|")
                print ""+str(kk[0])+" <---> "+str(kk[1])

        print "------------------"
	
	
##    while True:
##        time.sleep(5)
##
##        s = ""
##        f = open("streams/stream-"+time.strftime("%H:%M:%S"), 'a')
##
##
##        for k in stream_val.keys():
##            kk = k.split("|")
##            val = stream_val[k]
##            
##            s += kk[0]+" <> "+kk[1]+" -- "+str(val)+"\n\n"
##            
##            for i in streams[k]:
##                    s += str(i)+"\n\n"
##            
##            s += "---------------------------\n"
##            
##            
##            f.write(s)
##
##        f.close()
				
			

def stream_decider():
    """
        This thread will decide if a Stream is a stream or not

        Streams must be huge flows (TCP or UDP)

        HLS Stream must have: (TCP flows)
            |-> HTTP packets
            |-> HTTP GET for -audio and -video
            |-> HTTP response with content-type: application/vnd.apple.mpegurl
            |-> Has timestamps enabled
    """
    while True:
        time.sleep(5) #wait 5 seconds

        stream_amount_threshold = 100 #a stream must have at least THRESHOLD packets to be considered for a stream
        stream_score_threshold  = 4  #A stream must pass the score threshold to be considered a stream
        stream_time_threshold   = 2   #If a stream has too little packets, we check the time to decide if the stream will continue or not


        for k in stream_val.keys():
            if stream_val[k] == 0: #we will check only for the undecided streams
                stream = streams[k] #get the stream list for the k ip set
                
                if len(stream) >= stream_amount_threshold:
                    stream_score = 1 #the score that the stream gets (by product)

                    amt_timestamps  = 0 #amount of TCP packets that have timestamps enabled decremented by -1 for each packet that does not have timestamps enabled
                    amt_get_av      = 0 #amount of http requests that request audio and video
                    amt_content_tp  = 0 #amount of http responses with specific content type
                    amt_http        = 0 #must be greater than amt_content_tp + amt_get_av 
                    amt_clock       = 0 #must be equal to the amt_content_tp

                    #print "["+str(k)+"]"+" Checking streams "
                    
                    for s in stream:
                        #Check the streams one by one

                        #if a packet without timestamp is found, break
                        if s[HAS_TS] == False:
                            #print "["+str(k)+"]"+" No timestamps "
                            break

                        #count the number of GET_AV
                        if s[GET_AV]:
                            amt_get_av += 1

                        #count the number of content tupes
                        if s[CONTENT_TYPE]:
                            amt_content_tp += 1

                        #count the number of http packets
                        if s[IS_HTTP]:
                            amt_http += 1

                        #count the number of clocks
                        if len(s[CLOCK]) > 0:
                            amt_clock += 1

                    if amt_get_av == 0 or amt_get_av == 0 or amt_content_tp == 0 or amt_http == 0 or amt_clock == 0:
                        stream_score *= -1
                        #print "["+str(k)+"]"+" Not all options "
                    else:
                        stream_score *= 2
                        if abs(amt_clock - amt_content_tp) < 10: #ideally must be 0
                            stream_score *= 2
                        if abs(amt_content_tp - amt_get_av) < 10: #ideally must be 0
                            stream_score *= 2

                    if stream_score < 0:
                        stream_val[k] = -1
                    
                    #print "Stream: "+str(k)+" score: "+str(stream_score)

                    if stream_score >= stream_score_threshold:
                        stream_val[k] = 1

                else:
                    #Stream has too little packets, check the last packet time if the stream is continuing or not
                    ss = stream[-1] #get the last packet
                    t0 = ss[TIMESTAMP]
                    t1 = time.time()

                    #print "["+str(k)+"]"+" Less Packets "
                    
                    tt = t1-t0

                    if tt > stream_time_threshold:
                        stream_val[k] = -1
                        #print "["+str(k)+"]"+" Low packet count "
    
          

def manage_pckg(pack):
    """
        This handles the captured packets
        Get the TCP packets and format them to a 'stream' dictionary
        Another thread will decide if the stream IS a stream or not
    """
    if pack.haslayer("TCP"):

        stream_data = [0,0,0,0,0,0,0]

        stream_data[TIMESTAMP] = time.time()
        
        ip1 = pack[IP].src
        ip2 = pack[IP].dst

        ip = str(ip1)+"|"+str(ip2)
        temp_ip = str(ip2)+"|"+str(ip1)
        blacklisted = False
        is_stream = 0
    
    
    
        
        if stream_val.has_key(ip):
            #check if it is blacklisted

            is_stream = stream_val[ip]
            
            if stream_val[ip] == -1:
                #ip is blacklisted
                blacklisted = True
            
        elif stream_val.has_key(temp_ip):
            #Using the same IP's
            ip = temp_ip

            is_stream = stream_val[ip]
            
            if stream_val[ip] == -1:
                #ip is blacklisted
                blacklisted = True
            
        else:
            
            stream_val[ip] = 0 #undecided
            streams[ip] = [] #empty list
	

        if not blacklisted:
            
            stream_data[HAS_TS] = "Timestamp" in str(pack[TCP].options)

            if pack.haslayer(Raw):
                if "HTTP" in pack[Raw].load:
                    stream_data[IS_HTTP] = True

                    payload = pack[Raw].load

                    clock_t = []

                    if "Date" in payload:
                        #Extracting time:
                        s = payload

                        s = s.replace("\r", "|")
                        s = s.replace("\n", "|")
                        s = s.replace(":", "|")

                        t = s.split("|")

                        clock_t = (str(t[t.index('Date')+1])+" "+str(t[t.index('Date')+2])+" "+str(t[t.index('Date')+3])).strip().rstrip().replace(",", "").split(" ")

                    
                    stream_data[CLOCK] = clock_t
                    stream_data[GET_AV] = (("-audio" in payload) and ("-video" in payload))
                    stream_data[CONTENT_TYPE] = "Content-Type: application/vnd.apple.mpegurl" in payload
                else:
                    stream_data[IS_HTTP] = False
                    stream_data[CLOCK] = []
                    stream_data[GET_AV] = False
                    stream_data[CONTENT_TYPE] = False
            else:
                stream_data[IS_HTTP] = False
                stream_data[CLOCK] = []
                stream_data[GET_AV] = False
                stream_data[CONTENT_TYPE] = False
                
            end_t = time.time()
            stream_data[END_TIME] = end_t

            ll = streams[ip]
            ll.append(stream_data)
            
            streams[ip] = ll #add the data to the dictionary, if it exists python updates it
            stream_val[ip] = is_stream #Whether the stream IS a stream or it is undecided

#call threads:
decider_thread = threading.Thread(target=stream_decider)
printout_thread = threading.Thread(target=printout)

decider_thread.start()
printout_thread.start()

#call sniffer:
sniff(prn=manage_pckg, store=0)
