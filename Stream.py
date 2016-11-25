import time

class Stream:
    """
    This is the class that will handle a stream
    Stream is defined by two IP's
    src_ip | dest_ip
    ip1 | ip2
    """

    #ip1 = ""
    #ip2 = ""
    ips

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

    def __init__(self, ips, debug=0):
        self.ips = ips
        self._debugLevel = debug

        if self.debugLevel > 3:
            print("Stream ["+self.ip1+":"+self.ip2+"] initialized")

    def record_packet(self, timestamp, clock, av, cth, ctd):
        self.timestamps.push(timestamp)
        self.clocks.push(clock)
        self.av.push(av)
        self.content_type_hls.push(cth)
        self.content_type_dash.push(ctd)

        if cth:
            self.stream_type = self._HLS
        elif ctd:
            self.stream_type = self._DASH

        packetNr += 1

        self.recordedTime.push(time.time())

        if self.debugLevel > 2:
            print("Stream "+ip+" has a new packet")

        if self.debugLevel > 3:
            print(self.timestamps)
            print(self.clocks)
            print(self.av)
            if self.stream_type == self._HLS:
                print(self.content_type_hls)
            elif self.stream_type == self._DASH:
                print(self.content_type_dash)
            print(self.recordedTime)

        #call a thread to calculate delay and delay_average
