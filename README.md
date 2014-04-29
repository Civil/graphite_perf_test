graphite_perf_test
==================

Simple load testing utility for graphite

Originaly created by https://github.com/dkulikovsky
Modified to be multithreaded by me.

Example
==================

perf_test.py --destination=hostname --port=port --debug=1 --rate 75000x1000 -i 0 -s 10000x0 --threads=12
It will create 75M metrics/mintue (datapoints/minute), 75k TCP connections, 1k metrics each, load on host 'hostname'. Load will increase each iteration (-i 0), and will increase of 10000 connections (and 0 datapoints)
Load will be distributed equaly (on connection basis) for 12 threads.

Performacne
==================
1 Core, clocked at 1.7Ghz, of Core i7 Ivy Bridge (Mobile) can produce around 12M metrics per second. Around same is for 1core of Xeon E5645.