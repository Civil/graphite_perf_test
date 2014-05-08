graphite_perf_test
==================

Simple load testing utility for graphite

Originaly created by https://github.com/dkulikovsky
Modified to be multithreaded by me.

Example
==================

perf_test.py --destination=hostname --port=port --debug=1 --rate 75000x1000 -i 0 -s 10000x0 --threads=2 --duration=5

It will create 75M metrics/mintue (datapoints/minute), 75k TCP connections, 1k metrics each, load on host 'hostname'. Load will increase each iteration (-i 0), and will increase of 10000 connections (and 0 datapoints). This cycle will be repeated 5 times and in the end mean value and stddev for running time.
Load will be distributed equaly (on connection basis) for 2 threads.

Performacne
==================
1 Core of Ivy Bridge-E (Xeon E5-2650v2, 2.6GHz) capable to produce around 90M metrics per second.
