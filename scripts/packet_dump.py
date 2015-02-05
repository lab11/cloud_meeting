#!/usr/bin/env python

import IPy
import json
import sys
import time
import logging
import logging.handlers

try:
    import socketIO_client as sioc
except ImportError:
    print('Could not import the socket.io client library.')
    print('sudo pip install socketIO-client')
    sys.exit(1)

PROFILE_ID = 'ySYH83QLG2'

SOCKETIO_HOST = 'gatd.eecs.umich.edu'
SOCKETIO_PORT = 8082
SOCKETIO_NAMESPACE = 'stream'

if len(sys.argv) != 2:
    print('python packet_dump outfile')
    sys.exit(1)
log = logging.getLogger('packet_dump_log')
log.setLevel(logging.DEBUG)
log_filename = sys.argv[1] + '_'
handler = logging.handlers.TimedRotatingFileHandler(log_filename, when='midnight', backupCount=7)
log.addHandler(handler)

query = {'profile_id': PROFILE_ID}

class stream_receiver (sioc.BaseNamespace):
    def set_data (self, query, log, stream_namespace):
        self.query = query
        self.log = log
        self.stream_namespace = stream_namespace
        self.first_time = True

    def on_reconnect (self):
        if 'time' in query:
            del query['time']
        self.stream_namespace.emit('query', self.query)

    def on_connect (self):
        self.stream_namespace.emit('query', self.query)

    def on_data (self, *args):
        pkt = args[0]

        if self.first_time:
            log_data = ''
            self.first_time = False
            log_data += '#'
            for key in sorted(pkt.keys()):
                log_data += str(key) + ','
            log_data += '\n'
            log.info(log_data)

        log_data = ''
        for key in sorted(pkt.keys()):
            log_data += '"' + str(pkt[key]) + '",'
        log_data += '\n'
        log.info(log_data)


socketIO = sioc.SocketIO(SOCKETIO_HOST, SOCKETIO_PORT)
stream_namespace = socketIO.define(stream_receiver, '/{}'.format(SOCKETIO_NAMESPACE))
stream_namespace.set_data(query, log, stream_namespace)

socketIO.wait()

