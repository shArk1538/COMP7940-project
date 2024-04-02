import requests
import os

class HKBU_ChatGPT():
    def __init__(self):
        self.environ = os.environ

    def submit(self,message):

        URL = self.environ['GPT_BasicURL']
        ModelName = self.environ['GPT_ModelName']
        APIversion = self.environ['GPT_APIversion']
        Token = self.environ['GPT_Token']

        conversation = [{"role": "user", "content": message}]
        url = URL + "/deployments/" + ModelName + "/chat/completions/?api-version=" + APIversion
        headers = { 'Content-Type': 'application/json', 'api-key': Token }
        payload = { 'messages': conversation }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response


if __name__ == '__main__':
    ChatGPT_test = HKBU_ChatGPT()

    while True:
        
        user_input = input("Typing anything to ChatGPT:\t")
        response = ChatGPT_test.submit(user_input)
        print(response)

