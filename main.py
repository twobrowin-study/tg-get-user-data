import sys
from getpass import getpass

import asyncio

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.errors import UsernameNotOccupiedError
from telethon.errors import FloodWaitError
from telethon.tl.types import Channel

import dotenv, os, pandas

dotenv.load_dotenv()

# First you need create app on https://my.telegram.org
API_ID   = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
PHONE    = os.environ['PHONE']


async def get_chat_info(entity_str: str, client: TelegramClient) -> Channel:
    try:
        chat = await client.get_entity(entity_str)
    except UsernameNotOccupiedError:
        print('Chat/channel not found!')
        sys.exit()
    print(f"Found chat {chat}")
    return chat

async def dump_users(chat: Channel, client: TelegramClient):
    print('Process...')
    df = pandas.DataFrame([
        {
            'id':         user.id,
            'username':   user.username,
            'first_name': user.first_name,
            'last_name':  user.last_name,
        }
        async for user in client.iter_participants(chat)
    ])
    print('Done...')
    df.to_excel('users.xlsx')
    print('Saved...')


async def main():
    entity_str = input('Input a entity: ')
    client = TelegramClient('current-session', API_ID, API_HASH)
    print('Connecting...')
    await client.connect()
    if not await client.is_user_authorized():
        try:
            await client.send_code_request(PHONE)
            print('Sending a code...')
            await client.sign_in(PHONE, code=input('Enter code: '))
            print('Successfully!')
        except FloodWaitError as FloodError:
            print('Flood wait: {}.'.format(FloodError))
            sys.exit()
        except SessionPasswordNeededError:
            await client.sign_in(password=getpass('Enter password: '))
            print('Successfully!')
    await dump_users(await get_chat_info(entity_str, client), client)
    print('Done!')

if __name__ == '__main__':
    asyncio.run(main())