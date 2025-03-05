# generate pub and priv keys with ecddsda
# generate signature with ecddsda

import ecdsa
import pickle
import socket
import os


class __internal__ : 
    def generate_key():
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        return sk, vk

    def gen_keys(n) : 
        out = {}
        for a in range(n) : 
            sk, vk = __internal__.generate_key()
            out[a] = (sk, vk)
        return out        



def gen_sig(sk, message):
    sig = sk.sign(message)
    return sig

def ver_sig(vk, sig, message):
    return vk.verify(sig, message)

def dump_keys(n) :
    keys = __internal__.gen_keys(n)
    with open('keys.pkl', 'wb') as f:
        pickle.dump(keys, f)

def get_sock_fd() :
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", 0))
    sock_fd = sock.fileno()
    os.set_inheritable(sock_fd, True)
    return (sock, sock_fd)
