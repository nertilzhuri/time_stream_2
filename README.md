# Time Stream Algorithm <sub>Remastered</sub> #
- - - -

## Changes From First Algorithm

The algorithm will not use timers, the threads will check in real time for the packets and decide them.
This change will increase algorithm's performance

More modular code for easy management and maintenance (including debug levels).

## New Measurements

After implementation, the following measurements will be made:
* Time it takes to synchronize
* Minimum number of packets needed to synchronize
* Comparing Time and Minimum number of packets to NTP

## Security Improvements

* Checking whether the client asks for the stream
  * Prevents spoofing
  * Prevents stream simulations to change the time
>More TBA

## Analysis

### Performance

Changing the algorithm structure and filtering logic, it is calculated that a minimum number of **4 packets** is required to synchronize the time.

The NTP gathers NTP responses as samples to analyze them; according to NTP:

> Usually it takes about five minutes (five good samples) until a NTP server is accepted as synchronization source. Interestingly, this is also true for local reference clocks that have no delay at all by definition. <sup>1</sup>

Since delay affects the time, using more packets will yield to a more accurate time due to better delay calculation using more packets, so even though minimum 4 packets are needed, the more packets that are used the more accurate the time will be.

Comparing to NTP, the performance of this algorithm is superior since using only 4 stream packets the system will be able to synchronize the time with a minimal error (in our testing case using DIGITALB servers the error was -1 second).

### Security

Instead of filtering many packets and checking if the packets have the required components for it to be accepted as a art of the stream, here we also check if the Client IP is making requests for the Stream, thus making the algorithm more secure to attackers who may send fake streams without the client requesting.

The other security measures are also present: the algorithm will filter out any stream (block of IP's) that does not have the required components of a stream, so no network packet that is not part of a stream will be considered for time Synchronization

Since the algorithm does not use any special protocol, there is no dedicated communication for the time synchronization, the synchronization is done locally using captured stream packets, so any security measure used by the Streaming Server will be valid for the algorithm such as Spoofing the Network Stream.

More security measured against Spoofing (or any other time shifting attacks) will be prevented if the system is using more than one stream and cancel the streams with off time (using Marzullo's Algorithm)

In addition, the filtering of the packets can be made more extensive, using more filtering criteria or collecting more packets to analyze. Increase in filtering will have a performance cost since it will need more packets to decide a stream.

#### Server Security

All the above discussions are valid for the Servers, especially for the Streaming Servers, but there are additional discussions for the Servers that keep blocked ports (especially the NTP port) due to security measures.

The Servers even though have all the ports blocked, the HTTP port will be open for the Stream, which is enough to synchronize the time (provided the Server uses any Stream).

In short, there are no new protocols, communications, or ports that the algorithm uses; any existing security measure will be valid for this algorithm, moreover extensive filtering makes it even more secure against 'fake' streams.



## Implementations

- [x] Algorithm Design
- [x] Object Oriented Design
- [x] Removing Timers
- [x] Coding the sniffer
- [x] Coding the decider
- [x] Coding the Synchronization
- [x] Testing
- [x] Measuring Time
- [x] Measuring Minimum number of Packets
- [ ] Measure NTP (Wireshark)
- [x] Compare with NTP
- [x] Report (Check Analysis)

## References
- <sup>1</sup>[http://www.ntp.org/ntpfaq/NTP-s-algo.htm]
