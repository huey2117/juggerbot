import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import logging

import discord
from discord.ext import commands

log = logging.getLogger('jbot')
log.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='jbot.log', encoding='utf-8', mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
)

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
guild = os.getenv('DISCORD_GUILD')

# either client, client.run(token)
client = discord.Client()
# or bot, bot.run(token)
bot = commands.Bot(command_prefix='!')


@client.event
async def on_connect():
    """
    log connected status
    """
    for g in client.guilds:
        if g.name == guild:
            break
    log.info(f'{client.user} has connected to {g.name}')


@client.event
async def on_ready():
    """
    log ready status
    """
    for g in client.guilds:
        if g.name == guild:
            break

    log.info(f'{client.user} is ready on {g.name}')


@client.event
async def on_member_join(member):
    """
    On new user join, set them to X role which only allows them to view the
    #welcome channel. They will be required to respond to the Welcome Message
    with a reaction in order to access the rest of the discord.
    """
    await member.create_dm()
    await member.dm_channel.send('welcome message')


@client.event
async def on_error(event, *args, **kwargs):
    trace = sys.exc_info()[2]
    dt_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if event == 'on_message':
        log.error(f'Unhandled message: {args[0]}\n{trace}')
    else:
        raise


def main():
    client.run(token)


if __name__ == '__main__':
    main()
