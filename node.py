import socket
import os
import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some arguments.")
    parser.add_argument("--id", type=int, help="ID of the model.")
    parser.add_argument("--fd", type=int, help="File descriptors to receive.")
    parser.add_argument("--ports", type=json.loads, help="List of ports as JSON")
    parser.add_argument("--leader", type=int, help="Leader ID.")

    args = parser.parse_args()

    fd = os.dup(args.fd)
    sock = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
    os.close(args.fd)

    # start accepting connections to the  server.
    # if conn received and I am the leaer : 

    # Pre-prepare phase
    # sign the message and send it to all the other replicas



    print(f"Socket created on port {sock.getsockname()[1]} (FD duplicated)")
    print(f"ID: {args.id}")
    print(f"Ports: {args.ports}")

