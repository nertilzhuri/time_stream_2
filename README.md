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

## Implementations

- [x] Algorithm Design
- [x] Object Oriented Design
- [x] Removing Timers
- [x] Coding the sniffer
- [ ] Coding the Synchronization
- [ ] Testing
- [ ] Measuring Time
- [ ] Measuring Minimum number of Packets
- [ ] Measure NTP (Wireshark)
- [ ] Compare with NTP
- [ ] Report
