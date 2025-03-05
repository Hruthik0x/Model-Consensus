from ollama import chat
from ollama import ChatResponse

ques = 'Why is the sky blue?'

response: ChatResponse = chat(model='phi4', messages=[
  { 
    'role' : 'user',
    'content' : ques,
    # 'prompt': ques,
    # "stream": False,
  },
])

ans = response['message']['content']
print(ans)

prompt = '''
I will provide a conversation between an interviewer and an interviewee. Your task is to rate the interviewee's answer on a scale from 1 to 100, where a higher score indicates stronger agreement. Your response should be in the following format : 

<format>
    Index : {index}     
</format>

**Your response should not contain no other information or justification about the index other than the index (As mentioned in the format)**
'''

prompt += f"\n\nInterviewer: {ques} \n\n Inteervieweee: {ans}"

response: ChatResponse = chat(model='qwen2.5', messages=[
  {
    'role' : 'user',
    'content' : prompt,
  },
])

data = response['message']['content']
print("\n\n\n", data)