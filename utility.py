# generate pub and priv keys with ecddsda
# generate signature with ecddsda

import ecdsa
import pickle
import socket
import os
import ollama

MODELS = ["phi4", "gemma", "qwen2.5", "mistral"]
THRESHOLD = 80

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
    try:
        return vk.verify(sig, message)
    except ecdsa.BadSignatureError:
        return False

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


def get_ans(ques, model) : 
    model = MODELS[model]
    response: ollama.ChatResponse = ollama.chat(model=model, messages=[
        { 
            'role' : 'user',
            'content' : ques,
        },
    ])
    return response['message']['content']

def validate_ans(ques, ans, model) :
    model = MODELS[model]
    prompt = '''
    I will provide a conversation between an interviewer and an interviewee. Your task is to rate the interviewee's answer on a scale from 1 to 100, where a higher score indicates stronger agreement. Your response should be in the following format : 

    <format>
        Index : {index}     
    </format>

    **Your response should not contain no other information or justification about the index other than the index (As mentioned in the format)**
    '''

    prompt += f"\n\nInterviewer: {ques} \n\n Inteervieweee: {ans}"

    response: ollama.ChatResponse = ollama.chat(model='qwen2.5', messages=[
        {
            'role' : 'user',
            'content' : prompt,
        },
    ])

    data = response['message']['content']
    print(data)
    try : 
        data = int(data)
        print(data)
        return data >= THRESHOLD
    except :
        if data.find("Index") == -1 : 
            assert False, "Failed to extract the index"
        else : 
            index = data.split("Index : ")[1]
            index = int(index)
            print("INDEX", index)
            return index >= THRESHOLD