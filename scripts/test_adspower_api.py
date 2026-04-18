import asyncio
import json

async def test():
    # 测试1: 直接 GET 请求
    print("Test 1: GET request")
    cmd1 = ["curl", "-s", "http://127.0.0.1:50325/api/v1/user/list"]
    process = await asyncio.create_subprocess_exec(*cmd1, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    print("GET Result:", stdout.decode()[:300])
    
    # 测试2: POST 请求带 JSON body
    print("\nTest 2: POST with JSON body")
    cmd2 = ["curl", "-s", "-X", "POST", 
            "http://127.0.0.1:50325/api/v1/user/list",
            "-H", "Content-Type: application/json",
            "-d", '{"page":1,"page_size":10}']
    process = await asyncio.create_subprocess_exec(*cmd2, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    print("POST Result:", stdout.decode()[:300])
    
    # 测试3: 尝试用 aiohttp
    print("\nTest 3: aiohttp POST")
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post("http://127.0.0.1:50325/api/v1/user/list", 
                                json={"page": 1, "page_size": 10}) as resp:
            print("aiohttp Status:", resp.status)
            text = await resp.text()
            print("aiohttp Response:", text[:300])

asyncio.run(test())
