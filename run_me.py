import subprocess
import time
import json
import random
import socket
from utility import __internal__
from threading import Thread
# user defined
from utility import dump_keys, get_sock_fd, gen_sig

TEST_MODE = True

def handle_client(client) :
    data = client.recv(10000)
    if not data : 
        return
    print("Received data : " ,data)
    print("\n")


if __name__ == "__main__" :
    models_list = ["phi4", "gemma", "qwen2.5", "mistral"]
    # models_list = ["phi4"]Dd
    socks = []

    no_of_models = len(models_list)
    dump_keys(no_of_models)

    ports = []
    leader = random.randint(0, no_of_models-1)

    if TEST_MODE : 
        ports = [4000, 4001, 4002, 4003]
        leader = 2
        # print(leader)
    else :
        for a in range(no_of_models) : 
            sock, fd = get_sock_fd()
            socks.append(sock)
            ports.append(sock.getsockname()[1])

        for a in range(no_of_models) :

            subprocess.Popen(
                [
                    "python3", "node.py",
                    
                    "--id", str(a), 
                    "--fd", str(fd), 
                    "--ports", json.dumps(ports),
                    "--leader", str(leader),
                    "--client", str(3999)
                ],
                pass_fds=[fd],
                start_new_session=True
            )



    while True : 
        try : 
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("127.0.0.1", ports[leader]))
            query = input("Enter your query : ")

            send_data = {
                "ques" : query,
                "from" : "client",
            }
            send_data = json.dumps(send_data).encode('utf-8')
 
            sock.sendall(send_data)
            print("Sent query")
            break
        except Exception as e : 
            print(e)
            time.sleep(2)
            continue
        finally :
            sock.close()

    
    # open a socket server in a seperate thread 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 3999))
    sock.listen(5)
    while True : 
        client, addr = sock.accept()
        Thread(target=handle_client, args=(client,)).start()