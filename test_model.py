import ollama
import time

start = time.time()

response = ollama.chat(
    model="gemma3:4b",
    messages=[
        {
            "role": "user",
            "content": "What is Artificial Intelligence?"
        }
    ]
)

print(response["message"]["content"])

print("Time:", time.time() - start)