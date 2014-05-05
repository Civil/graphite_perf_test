#!/usr/bin/python -u
import socket
import sys
import time
import re
from math import sin
from optparse import OptionParser
from multiprocessing import Process, Queue
from random import random

DEBUG = 0
def log_queue(thread, lvl, msg):
    if re.match('debug', lvl.lower()):
        if not DEBUG:
            return
    queue.put("%s [%s][%s] %s" % (time.ctime(), thread, lvl.lower(), msg))
    return

def log_msg(lvl, msg):
    if re.match('debug', lvl.lower()):
        if not DEBUG:
            return
    print("%s [m][%s] %s" % (time.ctime(), lvl.lower(), msg))

def generate_load(connections, metrics, thread):
    ts = "%d" % time.time() 
    log_queue(thread, "debug", "New iteration...")
    for i in xrange(connections):
        out = ""
        for j in xrange(metrics):
            out += "%s.test%d.metric%d %s %s\n" % (options.prefix, i, j, random(), ts)
#            out += "%s.test%d.metric%d %s %s\n" % (options.prefix, i, j, sin(float(int(ts) + j)), ts)
        out += "\n\n"
        try:
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
            s.connect(addr)
            s.send(out)
            s.close()
        except Exception as e:
            log_queue(thread, "debug", "Failed to connecto to graphite on host %s, port %i: %s" % (options.dest, options.port, str(e)))

def output_log():
    while not queue.empty():
        print queue.get()


# get cli arguments
parser=OptionParser()
parser.add_option("-r",	"--rate", action="store", type="string", dest="rate", default="50x1000", help="Test rate. Format: CONNECTIONSxMETRICS, metrics means how much data sent in one connection")
parser.add_option("-d", "--destination", action="store", type="string", dest="dest", default="localhost", help="destination for performance test")
parser.add_option("-p", "--port", action="store", type="int", dest="port", default=2003, help="destination port")
parser.add_option("-s", "--step", action="store", type="string", dest="step", default="50x0", help="Increase load by CONNECTIONSxMETRICS")
parser.add_option("-i", "--interval", action="store", type="int", dest="interval", default=10, help="Load will be increased each INTERVAL iteration")
parser.add_option("-t", "--threads", action="store", type="int", dest="threads", default=1, help="How much threads will be executed, Connections will be splited via threads, but not metrics")
parser.add_option("--debug", action="store", type="int", dest="debug")
parser.add_option("--duration", action="store", type="int", dest="duration", help="Duration of the test. Default: unlimited")
parser.add_option("--prefix", action="store", type="string", dest="prefix", default="one_min.perf_test", help="prefix for metrics")
(options,args)=parser.parse_args()

queue = Queue()

step = options.step
time_step = options.interval

rate_re = re.compile(r'^([0-9]+)x([0-9]+)$')
m = rate_re.match(options.rate)
if m:
    connections = int(m.group(1))
    metrics = int(m.group(2))
else:
    log_msg("fatal","Failed to parse rate %s" % options.rate)
    sys.exit(1)

m = rate_re.match(options.step)
if m:
    connections_step = int(m.group(1))
    metrics_step = int(m.group(2))
else:
    log_msg("fatal", "Failed to parse step %s" % options.step)
    sys.exit(1)

if options.debug:
    DEBUG = 1

count = 0
g_count = 0
g_start_time = time.time()
addr = socket.getaddrinfo(options.dest, options.port, 0, 0, socket.SOL_TCP)[0][4]
workers = []

while 1:
    count += 1
    g_count += 1
    start_t = time.time()
    connections_per_thread = int(connections / options.threads)
    log_msg("debug", "Sending %d metrics to graphite, using %d threads, %d connections/thread" % (connections_per_thread * options.threads * metrics, options.threads, connections_per_thread))
    for i in range(0, options.threads):
        worker = Process(target = generate_load, args = (connections_per_thread, metrics, i))
        workers.append(worker)
        worker.start()

    for i in range(0, options.threads):
        workers[i].join()

    workers = []
    time_spent = float(time.time() - start_t)
    output_log()
    log_msg("debug", "Sending %d took %f" % (connections_per_thread * options.threads * metrics, time_spent))
    speed = connections * metrics / time_spent
    if time_spent < 60:
        sleep_time = float(60 - time_spent)
        time.sleep(sleep_time)
        log_msg("debug", "Slept for %f" % sleep_time)
        log_msg("debug", "Speed %f" % speed)
    else:
        log_msg("debug", "Overtime for %f" % (float(time_spent - 60.0)))
        overflow = (time_spent - 60) * speed
        log_msg("debug", "Speed %f, overflow %f" % (speed, overflow))

    if count >= time_step:
        connections += connections_step
        metrics += metrics_step
        log_msg("info", "Added [%d, %d] = %d, new size is [%d, %d] = %d" % (connections_step, metrics_step, connections_step * metrics_step, connections, metrics, connections * metrics))
        count = 0

    if options.duration and g_count > options.duration:
        log_msg("info", "Time limit %d exceded, current size %s" % (options.duration, size))
        sys.exit(0)
