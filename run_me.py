import subprocess
import time
import json
import random

# user defined
from utility import dump_keys, get_sock_fd


if __name__ == "__main__" :
    models_list = ["phi4", "gemma", "qwen2.5", "mistral"]
    # models_list = ["phi4"]Dd
    socks = []

    no_of_models = len(models_list)
    dump_keys(no_of_models)

    ports = []
    leader = random.randint(0, no_of_models-1)

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
            ],
            pass_fds=[fd],
            start_new_session=True
        )

    time.sleep(5)