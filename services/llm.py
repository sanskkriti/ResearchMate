import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def llm_call(prompt):
    response = client.chat.completions.create(
        model="llama3-70b-8192",  # You can change to llama3-8b for faster
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
