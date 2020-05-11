# TCP communication adapted from https://wiki.python.org/moin/TcpCommunication#Client

import bson
import json
import time
import socket
import pprint
import websocket
import argparse
import rospy
import datetime


def encode_message(msg):
    if TEST_MODE == JSON:
        return json.dumps(msg)
    elif TEST_MODE == BSON:
        return bson.BSON.encode(msg)


def decode_message(msg):
    if TEST_MODE == JSON:
        return json.loads(msg)
    elif TEST_MODE == BSON:
        bson_message = bson.BSON(msg)
        return bson_message.decode()


def websocket_send_wrapper(webs, data):
    if TEST_MODE == BSON:
        webs.send_binary(encode_message(data))
    else:
        webs.send(encode_message(data))


# Set up command line argument parser
parser = argparse.ArgumentParser(
    description='ROSBridge test client for JSON and BSON. Checks if a) the client can publish to a topic and b) if a service call can be made.')
serialization_group = parser.add_mutually_exclusive_group(required=False)
serialization_group.add_argument('--tcp', action="store_true", default=False)
serialization_group.add_argument(
    '--websocket', action="store_true", default=False)

communication_method_group = parser.add_mutually_exclusive_group(
    required=False)
communication_method_group.add_argument(
    '--json', action="store_true", default=False)
communication_method_group.add_argument(
    '--bson', action="store_true", default=False)

args = parser.parse_args()

print("BSON-ROSBridge Testclient")

# Setting up the constants for the different parameters
JSON = "JSON"
BSON = "BSON"
TCP = "TCP"
WEBSOCKET = "WEBSOCKET"

# Set the serialization method you want to test
# Warning: Might be overritten by CL arguments
# TEST_MODE = JSON
TEST_MODE = BSON

# Set the communication method you want to test
# Warning: Might be overritten by CL arguments
# COMMUNICATION_METHOD = TCP
COMMUNICATION_METHOD = WEBSOCKET

# Connection Parameters
TCP_IP = '0.0.0.0'
TCP_PORT = 9090
BUFFER_SIZE = 4096

# Websocket Parameters
WEBSOCKET_URL = "ws://"+TCP_IP+":"+str(TCP_PORT)

# Apply CL arguments, if necessary
if args.bson:
    TEST_MODE = BSON
elif args.json:
    TEST_MODE = JSON

if args.tcp:
    COMMUNICATION_METHOD = TCP
elif args.websocket:
    COMMUNICATION_METHOD = WEBSOCKET


# Prepare the messages to be sent
# This includes:
#  - Advertising a topic
#  - Publishing to it
#  - Sending a service request

advertise_msg = {
    "op": "advertise",
    "topic": "/bson_test",
    "type": "std_msgs/String"
}
my_message = {
    "data": "Hello from BSON-ROSBridge Testclient: "
}
if TEST_MODE == BSON:
    my_message["data"] += "BSON Mode via " + str(COMMUNICATION_METHOD)
elif TEST_MODE == JSON:
    my_message["data"] += "JSON Mode via " + str(COMMUNICATION_METHOD)

pub_msg = {
    "op": "publish",
    "topic": "/bson_test",
    "msg": my_message
}

call_service_params = {
    "a": 20,
    "b": 22
}

call_service_msg = {
    "op": "call_service",
    "service": "/add_two_ints",
    "args": call_service_params
}


if COMMUNICATION_METHOD == TCP:
    print("Testing TCP Communication")
    # TCP communication
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))

    if TEST_MODE == BSON:
        print("Sending BSON data")
        s.send(encode_message(advertise_msg))
        s.send(encode_message(pub_msg))
        s.send(encode_message(call_service_msg))
    elif TEST_MODE == JSON:
        print("Sending JSON data")
        s.send(encode_message(advertise_msg))
        # Add delay to cause message to be sent in separate tcp packets
        time.sleep(0.1)
        s.send(encode_message(pub_msg))
        # Add delay to cause message to be sent in separate tcp packets
        time.sleep(0.1)
        s.send(encode_message(call_service_msg))
    else:
        print("Invalid TEST_MODE")
        s.close()
        quit(1)

    data = s.recv(BUFFER_SIZE)
    print("Received " + TEST_MODE + " response over " + COMMUNICATION_METHOD + ":")
    pprint.pprint(decode_message(data))

    s.close()
elif COMMUNICATION_METHOD == WEBSOCKET:
    print("Testing Websocket Communication")
    ws = websocket.create_connection(WEBSOCKET_URL)
    i = 0
    # Filename to write
    filename = "save_log.txt"
    # Open the file with writing permission
    myfile = open(filename, 'w')
    # Write a line to the file
    myfile.write('--------------\n---- Test ----\n--------------\n')
    # Close the file
    myfile.close()
    while not rospy.is_shutdown():
        # begin clock
        first_time = datetime.datetime.now()
        # send request
        websocket_send_wrapper(ws, advertise_msg)
        websocket_send_wrapper(ws, pub_msg)
        websocket_send_wrapper(ws, call_service_msg)

        # receive response
        service_response = ws.recv()

        # stop clock
        later_time = datetime.datetime.now()

        # Compute time to receive response
        difference = later_time - first_time
        seconds_in_day = 24 * 60 * 60
        minute, second = divmod(
            difference.days * seconds_in_day + difference.seconds, 60)  # minutes, seconds

        # Print
        print("Received in: " + str(minute) + "m "+str(second) +
              "s"+" msg: " + TEST_MODE + " response :")
        pprint.pprint(decode_message(service_response))

        # Save logs
        myfile = open(filename, 'a')
        # Add the line
        data = "ok: "+str(minute)+"m"+str(second) + \
            "s\n" if (second < 8) else "pb: "+str(minute)+"m"+str(second)+"s\n"
        myfile.write(data)
        # Close the file
        myfile.close()
        i += 1


else:
    print("Invalid COMMUNICATION_METHOD")
    quit(1)
