import os
from dotenv import load_dotenv

import discord

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
guild = os.getenv('DISCORD_GUILD')

client = discord.Client()


@client.event
async def on_ready():
    for g in client.guilds:
        if g.name == guild:
            break

    print(f'{client.user} has connected to Discord!'
          f'{g.name}: {g.id}')

client.run(token)