import socket
import os
import argparse
import json
import threading
import pickle
import enum

import utility as utils


# Global vars - WIll avoid using them
NODE_ID = None
CUR_LEADER = None
PORTS = None
SOCK = None
CUR_PHASE = None 
KEYS = None

class Phase(enum.Enum) :
    PRE_PREPARE = 0
    PREPARE = 1
    COMMIT = 2

def verify_node(msg) :

    if len (msg) < 65 :
        return False
    
    node_id = int(msg[0])
    sig = msg[1:65]
    message = msg[65:]
    
    vk = KEYS[node_id][1]
    return utils.ver_sig(vk, sig, message)

def view_change() :
    global CUR_LEADER
    CUR_LEADER = (CUR_LEADER + 1) % len(PORTS)

def handle_client(client) :
    while True : 
        data = client.recv(1024)

        if not data : 
            break 

        if int(data[0]) == 0 :
            vk = data[1:66]
            msg = data[66:]
            if utils.ver_sig(vk, msg) : 
                if CUR_LEADER == NODE_ID : 
                    # start the pre-prepare phase
                    pass
                else :
                    # Forward the message to the leader
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(("127.0.0.1", PORTS[CUR_LEADER]))
                    sock.sendall(data)
                    sock.close()
            else :
                # assert False, "Invalid signature"
                pass 

        elif int(data) <= len(PORTS) :

            verify_node(data)
            msg = data[65:]
            req_type = int(msg[0])
            
            if req_type == Phase.PREPARE :
                pass
            elif req_type == Phase.COMMIT :
                pass
            else :
                pass 
                # assert False, "Invalid phase"

        else :
            pass
            # assert False, "Invalid node ID" 

def init() : 
    global NODE_ID, CUR_LEADER, PORTS, SOCK, KEYS
    parser = argparse.ArgumentParser(description="Process some arguments.")
    parser.add_argument("--id", type=int, help="ID of the model.")
    parser.add_argument("--fd", type=int, help="File descriptors to receive.")
    parser.add_argument("--ports", type=json.loads, help="List of ports as JSON")
    parser.add_argument("--leader", type=int, help="Leader ID.")

    args = parser.parse_args()

    fd = os.dup(args.fd)
    SOCK = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
    os.close(args.fd)

    NODE_ID = args.id
    CUR_LEADER = args.leader
    PORTS = args.ports

    KEYS = pickle.load(open('keys.pkl', 'rb'))

if __name__ == "__main__":
    data = pickle.load(open('keys.pkl', 'rb'))
    sig = data[0][0].sign(b"Hello")
    print(len(sig))
    print(utils.ver_sig(data[0][1], sig, b"Hello"))
    # init()

