import socket
import os
import argparse
import json
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

def verify_client(msg) :
    vk = msg[1:65]
    msg = msg[65:]
    return utils.ver_sig(vk, msg)

def view_change() :
    global CUR_LEADER
    CUR_LEADER = (CUR_LEADER + 1) % len(PORTS)

def handle_client(client) :
    while True : 
        data = client.recv(1024)

        if not data : 
            break 

        if int(data[0]) == 0 :
            if verify_client(data) :
                if CUR_LEADER == NODE_ID : 
                    cl_msg = data[65:]

                    l = len(data)
                    l = l.to_bytes(2, "little")

                    # start the pre-prepare phase

                    # msg[0:8] - request number - work on this :(
                    req_no = cl_msg[:8]
                    ques = cl_msg[8:]
                    ans = bytes(utils.get_ans(ques, NODE_ID).encode('utf-8'))
                    pack_dat = Phase.PRE_PREPARE.to_bytes(1, "little") + l + data + ans
                    sig = utils.gen_sig(KEYS[NODE_ID][0], pack_dat)
                    msg = NODE_ID.to_bytes(1, "little") + sig + pack_dat

                    for i in range(len(PORTS)) :
                        if i != NODE_ID :
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.connect("127.0.0.1", PORTS[i])
                            sock.sendall(msg)
                            sock.close()

                else :
                    # Forward the message to the leader
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(("127.0.0.1", PORTS[CUR_LEADER]))
                    sock.sendall(data)
                    sock.close()
            else :
                # assert False, "Invalid signature"
                pass 

        elif int(data[0]) <= len(PORTS) :
            if verify_node(data) :
                req_type = data[65]
                msg = data[66:]
                if req_type == Phase.PRE_PREPARE :
                    if data[0] == CUR_LEADER :
                        l = int.from_bytes(msg[:2], "little")
                        cl_dat = msg[2:2+l]
                        lead_ans = msg[2+l:]
                        verify_node(cl_dat)
                        cl_msg = cl_dat[65:]
                        req_no = cl_msg[:8]
                        ques = cl_msg[8:]
                        if utils.validate_ans(ques, lead_ans, NODE_ID) :
                            # send the prepare msg
                            dat = Phase.PREPARE.to_bytes(1, "little") + req_no
                            sig = utils.gen_sig(KEYS[NODE_ID], dat)
                            msg = NODE_ID.to_bytes(1, "little") + sig + dat
                            for i in range(len(PORTS)) : 
                                if i != NODE_ID : 
                                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    sock.connect("127.0.0.1", PORTS[i])
                                    sock.sendall(msg)
                                    sock.close()
                    else :
                        # assert False, "Invalid leader"
                        pass

                    # 4 = 3*1 + 1
                    # 4 = 3*x + 1
                    # x = 1
                    # no.of prepare msgs = 2f + 1 = 3

                elif req_type == Phase.PREPARE :
                    # Count no.of prepare messages received
                    # if recv 
                    # if recv more than 2f + 1 prepare messages, send commit messages
                    pass

                elif req_type == Phase.COMMIT :
                    pass

                else :
                    pass 
                    # assert False, "Invalid phase"
            else : 
                # assert False, "Invalid signature"
                pass 
        else :
            # assert False, "Invalid nodeID"
            pass 

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

