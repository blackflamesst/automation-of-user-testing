import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('AI_TOKEN')
)


async def ai_generate(text: str):
  completion = await client.chat.completions.create(
    model="deepseek/deepseek-chat",
    messages=[
    {
      "role": "user",
      "content": text
    }
  ]
)
  print(completion)
  return completion.choices[0].message.content