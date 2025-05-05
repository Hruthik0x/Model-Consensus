## Propmpt used : 
```
I will provide a conversation between an interviewer and an interviewee. Your task is to rate the interviewee's answer on a scale from 1 to 100, where a higher score indicates stronger agreement. Your response should be in the following format : 

<format>
    Index : {index}     
</format>

**Your response should not contain no other information or justification about the index other than the index (As mentioned in the format)**
```

## Models and their output :

| Model         | Extractable | Notes / Issues                                                            |
|---------------|--------|-----------------------------------------------------------------------|
| Gemma         | ✅     | -                                                                     |
| Phi4          | ✅     | Mentioned output along with the `<format>` tags                       |
| Mistral       | ✅     | Additional info mentioned after mentioning index                      |
| Qwen 2.5      | ✅     | -                                                                     |
| Deepseek-r1   | ❌     | i) Thinking tags are mentioned <br> ii) index returned as 10               |

## To-do

### Phase - 2

1) **Timeout** for each phase : 
    When sufficient messages are not received in the given time
    Consider, we didn't move to next phase, opt for view change,

2) **Replay attack** Each message received is logged, so if the node sends the same msg again, it 
   is simply ignored.


3) **Sync** after coming back online, send a sync request all other nodes, and then update to 2f+1 matching snapshot 


4) **View Change** (Reasons : Leader failure, network partition, etc)
    When one of the reasons mentioned happens,, then view change request is sent to every node.
    When a node receives sufficient view chnage requests, new leader is selected.
    The view change request consists of the current view number.
    New leader is cur_view_number + 1 % mod n.
    
5) **Causal ordering of messsages**
    If the view number of the received message : 
    - is smaller : ignore it
    -  is same : 
        - If the phase is smaller than current phase, then ignore it.
        - if higher phase, then cache / store it.  
    - is larger :
        - Keep recording msgs, if atleast 2f+1 higher matching view number from other nodes,
        then send the sync request

### Phase - 3 
1) **Export code base to solidity**
2) **Deploy it to blockchain network**

### Self notes : 

First connect ssd, mount it, check `$OLLAMA_MODELS`to verify if its pointing to the ssd    
```
sudo systemctl stop ollama
ollama serve
```