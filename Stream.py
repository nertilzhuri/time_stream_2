import time
import threading
import datetime

class Stream:
    """
    This is the class that will handle a stream
    Stream is defined by two IP's
    src_ip | dest_ip
    ip1 | ip2
    """

    ips = ""

    timestamps  = []
    clocks      = []
    delays      = []
    packetNr    = 0

    recordedTime = [] #Will be used to calculate delay (including processing)

    isStream = False
    blacklisted = False
    isSynchronizer = False

    av = [] #List of -audio and -video in payloar #HLS
    content_type_hls = [] #list of content_types for hls
    content_type_dash = [] #list of content_types for dash

    stream_type = 0;

    #constants
    _debugLevel = 0 #1, 2, 3
    _HLS = 0
    _DASH = 0

    #average calculator delays
    average_delay = 0
    delays = []

    #decider variables
    packetsChecked = 0

    #Hour synchronizer variables
    synced_hour = ""
    num_pckg = 0
    minimum_num_to_sync = -1

    #Threads
    #decider_thread = threading.Thread(target=self._decider)
    #clock_calculator_thread = threading.Thread(target=self._hourCalculate)

    def __init__(self, ips, debug=0):
        """
            The constructor that initializes this stream with the given ip
            Debug level is optional
        """
        self.ips = ips
        self._debugLevel = debug

        if self._debugLevel >= 3:
            print("Stream ["+self.ips+"] initialized")

        threading.Thread(target=self._decider).start()

    def record_packet(self, timestamp, clock, av, cth, ctd):
        self.timestamps.append(timestamp)
        self.clocks.append(clock)
        self.av.append(av)
        self.content_type_hls.append(cth)
        self.content_type_dash.append(ctd)

        if cth:
            self.stream_type = self._HLS
        elif ctd:
            self.stream_type = self._DASH

        self.packetNr += 1

        self.recordedTime.append(time.time())

        if self._debugLevel >= 2:
            print("Stream "+self.ips+" has a new packet")

        if self._debugLevel >= 3:
            print(self.timestamps)
            print(self.clocks)
            print(self.av)
            if self.stream_type == self._HLS:
                print(self.content_type_hls)
            elif self.stream_type == self._DASH:
                print(self.content_type_dash)
            print(self.recordedTime)

        #call a thread to calculate delay and delay_average

        if self.isStream:
            self._hourCalculate()

    def _calculateAverage(self):
        """
            This will be used as a thread to calculate the average of time
            Problem: Many threads will be open!
             Asynchronious call this function?
                |-> Problem: continuous call of the function!

            Call this function on new packet
        """

    def _decider(self):
        """
            Routinely check new packets as a thread
            Decide this stream

            Keep track of the checked packets
            Continue only with unchecked packets

            Do this until the packet is decided or blacklisted

            CHANGE: no check for HTTP, if stream has clocks, it has HTTP!
            CHANGE: no check for timestamps, the stream is automatically discarded for lack of timestamps

            The idea here is to find at least one of each 'Stream required' field
            which are listed below as variables, so if a stream has at least one of
            each we can decide it as a stream.

            The problem is that any spoofed packed that has any of these will be
            considered as a stream, and the attacked will wreack havoc

            The solutions for this are 2:
            1. Not checking the stream in general but checking as a two way communication
                |-> Check the packets that the client sends
                |-> Check the packets that the server responds
                |-> Check if the client is asking for the stream
            2. Running the algorithm and collecting data
                |-> Machine learning to determine optimal threasholds

            Using the first method yields to a more efficient algorithm

        """
        hasAV = False #Audio - Video
        hasCT = False #Content_Type
        hasCL = False #Clock

        if self._debugLevel >= 2:
            print "Decider Started for stream "+self.ips

        while not self.isStream and not self.blacklisted:
                #TODO: Check each list, filter

                #IDEA: Check the delay between packets, if too large, discard
                #IDEA: Check contents with threashold, if no (any) between a num. of packets, discard
                #IDEA: Upper one, if no (any) until the end, discard (requires min. nr. packets)
                #IDEA: Decide faster if all (any) are present -> Increase performance
                for i in range(self.packetsChecked, self.packetNr):
                    #self.timestamps.append(timestamp)
                    if len(self.clocks[i]) > 0:
                        hasCL = True

                    if self.av[i] == True:
                        hasAV = True

                    if self.stream_type == self._HLS or self.stream_type == self._DASH:
                        hasCT = True

                    self.packetsChecked = i

                    if hasCL and hasAV and hasCT:
                        self.decideStream()
                        break

    def _hourCalculate(self):
        """
            Will be called for each new packet after the stream is decided
        """
        clock_t = self.clocks[-1]

        if len(clock_t) <= 0:
            if self._debugLevel >= 3:
                print "Stream: "+self.ips+": Has no clock, waiting for next packet"
            return
        else:

            c_hour = clock_t[4]
            c_minute = clock_t[5]
            c_seconds = clock_t[6]

            c_time = ""+str(c_hour)+":"+str(c_minute)+":"+str(c_seconds)
            x = time.strptime(c_time,'%H:%M:%S')
            c_sec = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()

            #add the delay
            #c_sec += delay

            cc_time = str(datetime.timedelta(c_sec)) #to convert back
            self.synced_hour = c_time
            self.num_pckg = self.packetNr

            if self.minimum_num_to_sync < 0:
                self.minimum_num_to_sync = self.packetNr
                if self._debugLevel >= 1:
                    print "Stream: "+self.ips+": Successfully Synchronized clock"

            self.isSynchronizer = True

    def blacklist(self):
        """
            Function to clear up the stream if it is blacklisted
        """
        self.blacklisted = True

        self.timestamps = []
        self.clocks = []
        self.av = []
        self.content_type_hls = []
        self.content_type_dash = []
        self.packetNr = 0
        self.recordedTime = []

        if self._debugLevel >= 3:
            print("Stream "+str(self.ips)+" is blacklisted successfully!")

    def decideStream(self):
        """
            Clean up if possible
            Start the thread to calculate the hour

            NOTE: The hour calculation thread will not start from the begining
            until the stream is decided for security reasons
            Deciding the stream is equivalent to filtering it
        """
        self.isStream =True

        if self._debugLevel >= 1:
            print "Stream "+self.ips+" is DECIDED!"

        #TODO: Clean up not needed parts
        #clock_calculator_thread.start() #No need for thread
