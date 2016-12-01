import time
import threading

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

    av = [] #List of -audio and -video in payloar #HLS
    content_type_hls = [] #list of content_types for hls
    content_type_dash = [] #list of content_types for dash

    stream_type = 0;

    #constants
    _debugLevel = 0 #1, 2, 3
    _HLS = 0
    _DASH = 0

    #Threads
    clock_calculator_thread = threading.Thread(target=self._hourCalculate)

    def __init__(self, ips, debug=0):
        """
            The constructor that initializes this stream with the given ip
            Debug level is optional
        """
        self.ips = ips
        self._debugLevel = debug

        if self._debugLevel >= 3:
            print("Stream ["+self.ip1+":"+self.ip2+"] initialized")

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
        """
        while not self.isStream and not self.blacklisted:
                #TODO: Check each list, filter

                #IDEA: Check the delay between packets, if too large, discard
                #IDEA: Check contents with threashold, if no (any) between a num. of packets, discard
                #IDEA: Upper one, if no (any) until the end, discard (requires min. nr. packets)
                #IDEA: Decide faster if all (any) are present -> Increase performance

    def _hourCalculate(self):
        """
            Thread to calculate the hour from the stream
        """

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

        #TODO: Clean up not needed parts
        clock_calculator_thread.start()
