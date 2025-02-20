### Propmpt used : 
```
I will provide a conversation between an interviewer and an interviewee. Your task is to rate the interviewee's answer on a scale from 1 to 100, where a higher score indicates stronger agreement. Your response should be in the following format : 

<format>
    Index : {index}     
</format>

**Your response should not contain no other information or justification about the index other than the index (As mentioned in the format)**
```

### Models and their output :

| Model         | Extractable | Notes / Issues                                                            |
|---------------|--------|-----------------------------------------------------------------------|
| Gemma         | ✅     | -                                                                     |
| Phi4          | ✅     | Mentioned output along with the `<format>` tags                       |
| Mistral       | ✅     | Additional info mentioned after mentioning index                      |
| Qwen 2.5      | ✅     | -                                                                     |
| Deepseek-r1   | ❌     | i) Thinking tags are mentioned <br> ii) index returned as 10               |


### Possible leads : 
[Customizing Ollama](https://youtu.be/xa8pTD16SnM?si=R7-sraoLv6j7BLiw)

- Edit the system prompt (if any)
- Limiting the output length by tweaking the params


