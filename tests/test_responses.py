import aiohttp
import asyncio

BASE_URL = 'http://localhost:8000'  


async def test_create_person(session):
    async with session.post(f'{BASE_URL}/person/', json={
        "name": "John Doe",
        "email": "john@example.com",
        "email_verified": True
    }) as response:
        json_response = await response.json()
        print('POST /person:', json_response, response.status)

async def test_get_persons(session):
    async with session.get(f'{BASE_URL}/person/') as response:
        json_response = await response.json()
        print('GET /person:', json_response, response.status)

async def test_get_person_by_id(session, person_id):
    async with session.get(f'{BASE_URL}/person/{person_id}') as response:
        json_response = await response.json()
        print(f'GET /person/{person_id}:', json_response, response.status)

async def test_update_person(session, person_id):
    async with session.put(f'{BASE_URL}/person/{person_id}', json={
        "name": "Jane Doe",
        "email": "jane@example.com"
    }) as response:
        json_response = await response.json()
        print(f'PUT /person/{person_id}:', json_response, response.status)

async def test_patch_person(session, person_id):
    async with session.patch(f'{BASE_URL}/person/{person_id}', json={
        "email_verified": False
    }) as response:
        json_response = await response.json()
        print(f'PATCH /person/{person_id}:', json_response, response.status)

async def test_delete_person(session, person_id):
    async with session.delete(f'{BASE_URL}/person/{person_id}') as response:
        print(f'DELETE /person/{person_id}:', response.status)

async def test_options_person(session):
    async with session.options(f'{BASE_URL}/person/') as response:
        json_response = await response.json()
        print('OPTIONS /person:', json_response, response.status)

async def test_head_person(session):
    async with session.head(f'{BASE_URL}/person/') as response:
        print('HEAD /person:', response.status)

async def main():
    async with aiohttp.ClientSession() as session:
        await test_create_person(session)
        await test_get_persons(session)
        await test_get_person_by_id(session, person_id=1)
        await test_update_person(session, person_id=1)
        await test_patch_person(session, person_id=1)
        await test_delete_person(session, person_id=1)
        await test_options_person(session)
        await test_head_person(session)


if __name__ == '__main__':
    asyncio.run(main())

