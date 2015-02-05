#!/usr/bin/env python2

import IPy
import json
import sys
from threading import Thread
import Queue
import time
import random
import os
import urllib2
from copy import copy
try:
    import assigned_numbers_utility as anutil
except ImportError:
    sys.path.insert(0, "../scripts")
    try:
        import assigned_numbers_utility as anutil
    except ImportError:
        print("Problem importing assigned_numbers_utility from the scripts folder.")
        print("Make sure either scripts is on your path or you're running me from bleServiceStreamer.")

try:
    import socketIO_client as sioc
except ImportError:
    print('Could not import the socket.io client library.')
    print('sudo pip install socketIO-client')
    sys.exit(1)

import logging
import logging.handlers

BLEADDR_PROFILE_ID = 'ySYH83QLG2'
BLESERVICE_PROFILE_ID = '9GmxTr7IuI'

BLEADDR_EXPLORE_ADDR = 'http://gatd.eecs.umich.edu:8085/explore/profile/' + BLEADDR_PROFILE_ID
BLESERVICE_POST_ADDR = 'http://gatd.eecs.umich.edu:8081/' + BLESERVICE_PROFILE_ID


def main( ):

    # setup logging
    log = logging.getLogger('bleServiceStreamer_log')
    log.setLevel(logging.DEBUG)
    log_filename = 'logs/bleServiceStreamer_log.out'
    handler = logging.handlers.TimedRotatingFileHandler(log_filename,
            when='midnight', backupCount=7)
    log.addHandler(handler)
    log.info("Running BLE service streamer ...")
    print("Running BLE service streamer controller...")

    # start threads to receive data from GATD
    message_queue = Queue.Queue()
    ReceiverThread(BLEADDR_PROFILE_ID, {}, 'bleAddr', message_queue)

    # start presence controller
    controller = ServiceController(message_queue, BLESERVICE_POST_ADDR, log)
    controller.monitor()

def post_to_gatd(data, address, log=None):
    try:
        req = urllib2.Request(address)
        req.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(req, json.dumps(data))
    except (httplib.BadStatusLine, ullib2.URLError), e:
        # ignore error and carry on
        if log:
            log.error(curr_datetime() + "ERROR - Post to GATD: " + str(e))
        else:
            print(curr_datetime() + "ERROR - Post to GATD: " + str(e))

def curr_datetime():
    return time.strftime("%m/%d/%Y %H:%M:%S ")


class ServiceController ():

    def __init__(self, queue, post_address, log):
        self.msg_queue = queue
        self.log = log
        self.post_address = post_address

        self.last_packet = 0
        self.start_time = time.time()

        self.last_gatd_post = {}

    def monitor(self):
        while True:

            data_type = 'None'
            pkt = None
            try:
                # wait for data from GATD
                [data_type, pkt] = self.msg_queue.get(timeout=5)
            except Queue.Empty:
                # No data has been seen, timeout to update presences
                pass

            # print stuff to the screen
            #self.update_screen()

            # check data for validity
            if (pkt == None or 'location_str' not in pkt or 'time' not in pkt):
                continue

            # packet is definitely valid
            self.last_packet = time.time()

            # handle bleAddr data
            if data_type == 'bleAddr':
                #Process packets here        
                print(pkt['name'])
                print(pkt['ble_addr'])
                payload = pkt['payload'][6:]
                #print(self.hex_str_payload(payload))
                gap_data = self.decoded_gap_data(self.get_gap_data(payload))
                for field in gap_data:
                    if type(field["data"]) == type(""):
                        print("{0}: {1}".format(field["name"], field["data"]))
                    else:
                        field["data"].reverse() #big endian like god intended
                        print("{0}: {1}".format(field["name"], self.hex_str_payload(field["data"])))
                print("\n")

                # eventually send things to GATD...
                #data = {'location_str': pkt['location_str']}
                #post_to_gatd(data, self.post_address, self.log)

    def hex_str_payload(self, payload):
        hex_payload = ""
        for byte in payload:
            hex_payload += "{:02x} ".format(byte)
        return hex_payload

    def get_gap_data(self, payload):
        gap_data = []
        buf = copy(payload)
        while len(buf) > 3:
            gap_data_type = []
            num_bytes = buf.pop(0)
            for i in range(num_bytes):
                byte = buf.pop(0)
                gap_data_type.append(byte)
            gap_data.append(gap_data_type)
        return gap_data

    # This should be done programmatically off of the online SIG documents
    def decoded_gap_data(self, gap_data):
        decoded_gap_data = []
        for field in gap_data:
            decoded_field = {}
            name = ""
            field = copy(field)
            data_type = field.pop(0)
            try:
                name = anutil.get_gap_data_type_name(data_type)
                if name == "Shortened Local Name" or name == "Complete Local Name":
                    data = ""
                    for char in field:
                        data += chr(char)
                else:
                    data = field
            except:
                name = data_type
                data = field
            decoded_field = {"name": name, "data": data}
            decoded_gap_data.append(decoded_field)
        return decoded_gap_data

            

    def update_screen(self):
        # only update once per second at most
        if (time.time() - self.last_update) > 1:
            self.last_update = time.time()
            
            # clear terminal screen
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Time: " + time.strftime("%I:%M:%S") +
                    '\t\t\tLast packet ' + str(int(round(time.time() - self.last_packet))) + 
                    ' seconds ago' +
                    '\t\tStarted ' + str(int(round(time.time() - self.start_time))) +
                    ' seconds ago')

            # print devices by uniqname
            #MEGHAN: Print stuff here if you want anything printed


class ReceiverThread (Thread):
    SOCKETIO_HOST = 'gatd.eecs.umich.edu'
    SOCKETIO_PORT = 8082
    SOCKETIO_NAMESPACE = 'stream'

    def __init__(self, profile_id, query, data_type, message_queue):

        # init thread
        super(ReceiverThread, self).__init__()
        self.daemon = True

        # init data
        self.profile_id = profile_id
        self.data_type = data_type
        self.message_queue = message_queue
        self.stream_namespace = None

        # make query. Note that this overrides the profile id with the user's
        #   choice if specified in query
        profile_query = {'profile_id': profile_id}
        self.query = dict(list(profile_query.items()) + list(query.items()))

        # start thread
        self.start()

    def run(self):
        while True:
            try:
                socketIO = sioc.SocketIO(self.SOCKETIO_HOST, self.SOCKETIO_PORT)
                self.stream_namespace = socketIO.define(StreamReceiver,
                        '/{}'.format(self.SOCKETIO_NAMESPACE))
                self.stream_namespace.set_data(self.query, self.data_type,
                        self.message_queue, self.stream_namespace)
                socketIO.wait()
            except sioc.exceptions.ConnectionError:
                # ignore error and continue
                socketIO.disconnect()


class StreamReceiver (sioc.BaseNamespace):

    def set_data (self, query, data_type, message_queue, stream_namespace):
        self.query = query
        self.data_type = data_type
        self.message_queue = message_queue
        self.stream_namespace = stream_namespace

    def on_reconnect (self):
        if 'time' in query:
            del query['time']
        self.stream_namespace.emit('query', self.query)

    def on_connect (self):
        self.stream_namespace.emit('query', self.query)

    def on_data (self, *args):
        # data received from gatd. Push to msg_q
        self.message_queue.put([self.data_type, args[0]])


if __name__=="__main__":
    main()

