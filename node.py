import socket
import os
import argparse     
import json
import pickle
import enum
import utility as utils
import threading

# DEBUG_MODE = True
DEBUG_MODE = False

MAX_BACKLOG_CONNS = 5

def log(msg, self_id) :
    with open(f"./logs/node_{self_id}.log", "a") as f :
        f.write(msg + "\n")

class Phase(enum.Enum) :
    PRE_PREPARE = 0
    PREPARE = 1
    COMMIT = 2
    VIEW_CHANGE = 3

def verify_node_data(data, sys_data) :
    node_id = int(data["from"])
    sig = bytes.fromhex(data["sig"])

    # made a copy to remove the signature
    data_cpy = data.copy()
    del data_cpy["sig"]
    message = json.dumps(data_cpy).encode('utf-8')
    vk = sys_data.keys[node_id][1]
    return utils.ver_sig(vk, sig, message)

def handle_client(client, sys_data) :

    while True : 

        data = client.recv(10000)

        if not data : break

        data = json.loads(data.decode('utf-8'))         

        if data["from"] == "client" :

            # If I am the leader, then I will process the request
            # ledaer id is nothing but view number
            
            if sys_data.self_id == sys_data.leader_id : 
                
                log(f"Received query from client : {data['from']} \nLeader generating answer, could take a while\n", sys_data.self_id)
                
                if DEBUG_MODE : 
                    ans = "Dummy answer"
                else :
                    ans = str(utils.get_ans(data["ques"], sys_data.self_id))
                # ans = "There are 2 'r's in the word \"strawberry\""

                sys_data.ans = ans
                sys_data.ques = data["ques"]
                sys_data.seq_no += 1

                log(f"Answer generated : \n```\n{ans}\n```", sys_data.self_id)

                send_data = {
                                "phase"  : Phase.PRE_PREPARE.value,
                                "seq_no" : sys_data.seq_no,
                                "view_no": sys_data.view_no,
                                "digest" : utils.get_digest(data["ques"]),
                                "ques"   : data["ques"],
                                "ans"    : ans,
                                "from"   : sys_data.self_id,
                            }
                
                sig = utils.gen_sig(sys_data.keys[sys_data.self_id][0], json.dumps(send_data).encode('utf-8'))
                send_data["sig"] = sig.hex()
                send_data_bytes = json.dumps(send_data).encode('utf-8')

                for i, port_num in enumerate(sys_data.ports) :
                    if i != sys_data.self_id :
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect(("127.0.0.1", port_num))
                        sock.sendall(send_data_bytes)
                        sock.close()
                
                # sys_data.received_pre_prep = send_data
                log("Sent pre-prepare msg", sys_data.self_id)

            # If I am not the leader, then I will send the request to the leader
            else :

                # convert data back to bytes
                data = json.dumps(data).encode('utf-8')

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(("127.0.0.1", sys_data.ports[sys_data.leader_id]))
                sock.sendall(data)
                sock.close()

        # Valid node ID
        elif data["from"] < len(sys_data.ports) :

            # verifies the signature
            if verify_node_data(data, sys_data) :

                if data["view_no"] == sys_data.view_no :
 
                    if data["phase"] == Phase.PRE_PREPARE.value :

                        if data["from"] != sys_data.leader_id :
                            log("Error : Received pre-prepare message from non-leader", sys_data.self_id)
                            continue 
                        

                        log(f"Received pre-prepare msg from {data['from']}", sys_data.self_id)

                        if data["seq_no"] == sys_data.seq_no + 1:


                            sys_data.ques = data["ques"]
                            sys_data.ans = data["ans"]
                            sys_data.seq_no = data["seq_no"]

                            send_data = {
                                "phase"  : Phase.PREPARE.value,
                                "seq_no" : data["seq_no"],
                                "view_no": data["view_no"],
                                "digest" : data["digest"],
                                "from"   : sys_data.self_id,
                            }

                            sig = utils.gen_sig(sys_data.keys[sys_data.self_id][0], json.dumps(send_data).encode('utf-8'))
                            send_data["sig"] = sig.hex()
                            send_data_bytes = json.dumps(send_data).encode('utf-8')

                            del send_data["sig"]
                            del send_data["from"]
                            sys_data.received_pre_prep = send_data

                            for i, port_num in enumerate(sys_data.ports) :
                                if i != sys_data.self_id and i != sys_data.leader_id :
                                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    sock.connect(("127.0.0.1", port_num))
                                    sock.sendall(send_data_bytes)
                                    sock.close()



                            log("Sent prepare msg" , sys_data.self_id)

                    elif data["phase"] == Phase.PREPARE.value :

                        log(f"Received prepare msg from {data['from']}", sys_data.self_id)

                        # | Term                                  | Count    |
                        # | ------------------------------------- | -------- |
                        # | Pre-Prepare from leader               | 1        |
                        # | Prepare messages needed from others   | 2f − 1   |
                        # | + own Prepare (counted locally)       | 1        |
                        # | Total matching messages to proceed    | 2f + 1   |

                        del data["sig"]
                        del data["from"]

                        # Have to apply causal orderning over here, what if I get prepare msgs, before 
                        # I get pre - prepare msg ? 
                        # in such case sys_data.received_pre_prep will not match data
                        
                        # I have to update 2*f - 1 to 2f and put sys_data.matching_prep += 1 in prepare phase 
                        # I can stall here, if matching_prep == 0, wait for it to get updated 
                        # when matching_prep is 1, i,e when I have received pre-prepare msg
                        # I can proceed with the prepare phase ...
                        
                        
                        if data == sys_data.received_pre_prep : 
                            sys_data.matching_prep += 1

                            if sys_data.matching_prep >= 2 * sys_data.max_f - 1 and sys_data.waiting_for_prep:

                                sys_data.waiting_for_prep = False

                                log(f"Received enough prepare messages", sys_data.self_id)
                                log(f"Validating ans, it could take a while", sys_data.self_id)

                                if DEBUG_MODE or utils.validate_ans(sys_data.ques, sys_data.ans, sys_data.self_id) : 

                                    #prepare stuff for commit_phase
                                    send_data = {
                                        "phase"  : Phase.COMMIT.value,
                                        "seq_no" : data["seq_no"],
                                        "view_no": data["view_no"],
                                        "from"   : sys_data.self_id,
                                    }

                                    sig = utils.gen_sig(sys_data.keys[sys_data.self_id][0], json.dumps(send_data).encode('utf-8'))
                                    send_data["sig"] = sig.hex()
                                    send_data_bytes = json.dumps(send_data).encode('utf-8')

                                    sys_data.commit_msgs_cnt += 1

                                    for i, port_num in enumerate(sys_data.ports) :
                                        if i != sys_data.self_id :
                                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                            sock.connect(("127.0.0.1", port_num))
                                            sock.sendall(send_data_bytes)
                                            sock.close()

                                    log(f"Sent commit msg", sys_data.self_id)


                                    # Case : if it receives commit messages from others before it could send commit messages 
                                    # need for causal ordering over here for better performance

                                    if sys_data.commit_msgs_cnt >= 2 * sys_data.max_f + 1 :

                                        log(f"Received enough commit messages", sys_data.self_id)

                                        send_data = {
                                            "ans" : sys_data.ans,
                                            "from" : sys_data.self_id,
                                        }

                                        sig = utils.gen_sig(sys_data.keys[sys_data.self_id][0], json.dumps(send_data).encode('utf-8'))
                                        send_data["sig"] = sig.hex()
                                        send_data_bytes = json.dumps(send_data).encode('utf-8')
                                        # send the ans to client

                                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                        sock.connect(("127.0.0.1", sys_data.client_port))
                                        sock.sendall(send_data_bytes)
                                        sock.close()

                                        # Simulate wriiting it in local ledger or something.
                                        # Perform cleanup
                                        sys_data.commit_msgs_cnt = 0
                                        sys_data.matching_prep = 0
                                        sys_data.received_pre_prep = {}
                                        sys_data.ques = ""
                                        sys_data.ans = ""
                                        sys_data.waiting_for_prep = True


                                        # View change - local, have to implement consensus view change - Pending
                                        sys_data.view_no += 1
                                        sys_data.leader_id = (sys_data.leader_id + 1) % len(sys_data.ports)


                        else : 
                            log("Error : Invalid prepare message", sys_data.self_id)
                            log(f"Expected : {sys_data.received_pre_prep}", sys_data.self_id)
                            log(f"Received : {data}", sys_data.self_id)

                    elif data["phase"] == Phase.COMMIT.value :

                        log(f"Received commit msg from {data['from']}", sys_data.self_id)

                        sys_data.commit_msgs_cnt += 1
                        if sys_data.commit_msgs_cnt >= 2 * sys_data.max_f + 1  :

                            log(f"Received enough commit messages", sys_data.self_id)

                            send_data = {
                                "ans" : sys_data.ans,
                                "from" : sys_data.self_id,
                            }

                            sig = utils.gen_sig(sys_data.keys[sys_data.self_id][0], json.dumps(send_data).encode('utf-8'))
                            send_data["sig"] = sig.hex()
                            send_data_bytes = json.dumps(send_data).encode('utf-8')
                            # send the ans to client

                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.connect(("127.0.0.1", sys_data.client_port))
                            sock.sendall(send_data_bytes)
                            sock.close()

                            # Simulate wriiting it in local ledger or something.
                            # Perform cleanup
                            sys_data.commit_msgs_cnt = 0
                            sys_data.matching_prep = 0
                            sys_data.received_pre_prep = {}
                            sys_data.ques = ""
                            sys_data.ans = ""
                            sys_data.waiting_for_prep = True


                            # View change - local, have to implement consensus view change - Pending
                            sys_data.view_no += 1
                            sys_data.leader_id = (sys_data.leader_id + 1) % len(sys_data.ports)

                    else : 
                        log("Error : Invalid phase", sys_data.self_id)

                elif data["view_no"] < sys_data.view_no :
                    # Just ignore it as its an old message
                    pass 

                else : 
                    # Request for synchronization.
                    # have to implement - Pending
                    pass

                    # assert False, "Invalid phase"
            else : 
                log("Error : Signature verification failed", sys_data.self_id)
                # assert False, "Invalid signature"
                pass 
        else :
            log("Error : Invalid node ID", sys_data.self_id)
            # assert False, "Invalid nodeID"
            pass 

class System_data () : 

    def __init__ (self, self_id, leader_id, ports, keys, client_port) : 
        self.self_id = self_id
        self.leader_id = leader_id
        self.ports = ports
        self.keys = keys
        self.client_port = client_port
        self.view_no = leader_id

        # other default values 
        self.max_f = (len(ports) - 1) // 3
        self.seq_no = 0
        self.matching_prep = 0
        self.received_pre_prep = {}
        self.ques = ""
        self.ans = ""
        self.commit_msgs_cnt = 0

        self.waiting_for_prep = True


def init() : 
    parser = argparse.ArgumentParser(description="Process some arguments.")
    
    parser.add_argument("--client", type=int, help="Client port.")
    parser.add_argument("--ports", type=json.loads, help="List of ports as JSON")
    parser.add_argument("--leader", type=int, help="Leader ID.")
    parser.add_argument("--id", type=int, help="ID of the model.")

    args = parser.parse_args()

    sys_data = System_data(args.id, 
                           args.leader, 
                           args.ports, 
                           pickle.load(open('keys.pkl', 'rb')), 
                           args.client)

    
    # Cleaning up the log file before starting
    with open(f"./logs/node_{sys_data.self_id}.log", "w") as f :
        f.write("")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock .bind(("127.0.0.1", sys_data.ports[sys_data.self_id]))

    sock.listen(MAX_BACKLOG_CONNS)
    
    while True : 
        client, _ = sock.accept()
        threading.Thread(target=handle_client, args=(client, sys_data)).start()

if __name__ == "__main__":
    init()


# python3 node.py --ports [4000,4001,4002,4003] --leader 2 --client 3999 --id 0