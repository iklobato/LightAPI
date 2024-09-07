---
title: Testing Handlers
---

You can test the handlers directly without relying on a live server by using Python’s `aiohttp` client to simulate requests.

### Sample script to test all endpoints:

``` py
import aiohttp
import asyncio

BASE_URL = 'http://localhost:8080'

async def test_endpoints():
    async with aiohttp.ClientSession() as session:
        await session.post(f'{BASE_URL}/person/', json={ "name": "John Doe", "email": "john@example.com", "email_verified": True })
        await session.get(f'{BASE_URL}/person/')
        await session.get(f'{BASE_URL}/person/1')
        await session.put(f'{BASE_URL}/person/1', json={ "name": "Jane Doe", "email": "jane@example.com" })
        await session.patch(f'{BASE_URL}/person/1', json={ "email_verified": False })
        await session.delete(f'{BASE_URL}/person/1')
        await session.options(f'{BASE_URL}/person/')
        await session.head(f'{BASE_URL}/person/')

if __name__ == '__main__':
    asyncio.run(test_endpoints())
```
