import os
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="rpa_3I7F4NH6UOAWV8KMWMIO8QPT1L5XW5VL5122VEUK1vr02z",
    base_url="https://api.runpod.ai/v2/8xamd8vr47kl2d/openai/v1",
)


async def llm_generate(prompt: str) -> str:
    """Generate text using OpenAI API asynchronously"""
    response = await client.chat.completions.create(
        model="Qwen/Qwen2-VL-7B-Instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.1,
        top_p=0.95
    )
    return response.choices[0].message.content.strip()

    