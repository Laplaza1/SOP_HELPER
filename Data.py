import os


import httpx
from openai import OpenAI

client = OpenAI(
    api_key=token,
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(
        3600.0
    ),  # Override default timeout with longer timeout for reasoning models
)


class Account:

    def __init__(self, name: str, serviceLevel, SOPs: list[set[(str, list)]]):
        self.name = name
        self.serviceLevel = serviceLevel
        self.customerID = None
        self.SOPs = SOPs

    def add_sop(self, new_sop):
        self.SOPs.append(new_sop)

    def remove_sop(self, index):
        self.SOPs.pop(index)

    def change_index(self):
        pass


user1 = Account(
    "Bill",
    1,
    [
        {
            "Cook Eggs": [
                "Break Egg",
                "Put on Mid-heat Skillet",
                "Wait until egg solidifies",
                "Move Egg to plate",
            ]
        }
    ],
)


user1.add_sop({"Open Door": ["Twist knob", "push forward"]})

print(user1.SOPs)
print(user1.remove_sop(1))
print(user1.SOPs)


def chat():
    response = client.responses.create(
        model="grok-4",
        input=[
            {
                "role": "system",
                "content": "You are Grok, an AI agent built to answer helpful questions.Focus your responses to utilize the SOPs",
            },
            {
                "role": "user",
                "content": f"From the SOPs {user1.SOPs} please tell me what to do after I buy an egg at the store",
            },
        ],
    )
    return response.output_text
