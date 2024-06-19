from aiohttp import ClientSession
import json
import asyncio

class GPT35TurboChat:
    url = "https://www.chatgpt-free.cc"
    model = "gpt-3.5-turbo"

    async def chat_with_gpt35_turbo(self, messages):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Accept": "text/event-stream",
            "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Referer": "https://chat.fstha.com/",
            "x-requested-with": "XMLHttpRequest",
            "Origin": "https://chat.fstha.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Authorization": "Bearer ak-chatgpt-nice",
            "Connection": "keep-alive",
            "Alt-Used": "chat.fstha.com",
        }

        async with ClientSession(headers=headers) as session:
            data = {
                "messages": messages,
                "stream": True,
                "model": self.model,
            }
            async with session.post(f"{self.url}/api/openai/v1/chat/completions", json=data) as response:
                response.raise_for_status()
                async for chunk in response.content:
                    if chunk.startswith(b"data: [DONE]"):
                        break
                    if chunk.startswith(b"data: "):
                        content = json.loads(chunk[6:])["choices"][0]["delta"].get("content")
                        if content:
                            yield content

# Example usage
async def main():
    chatbot = GPT35TurboChat()
    async for response in chatbot.chat_with_gpt35_turbo(["Hello, how are you?"]):
        print(response)

# Run the async function
try:
    asyncio.run(main())
except Exception as e:
    print(f"An error occurred: {e}")