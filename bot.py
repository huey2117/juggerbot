import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import logging

import discord
from discord.ext import commands

logging.basicConfig(
    filename='jbot.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
target_guild = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.presences = True
intents.members = True

# either client, client.run(token)
# client = discord.Client()
# or bot, bot.run(token)
client = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def on_connect():
    """
    log connected status
    """
    logging.info(f'{client.user} is connected')


@client.event
async def on_ready():
    """
    log ready status
    """
    for guild in client.guilds:
        if guild.name == target_guild:
            break

    logging.info(f'{client.user} is ready on {guild.name}')


@client.event
async def on_member_join(member):
    """
    On new user join, set them to a role which only allows them to view the
    #welcome channel. They will be required to respond to the Welcome Message
    with a reaction in order to access the rest of the discord.
    """
    role = discord.utils.get(member.guild.roles, name='Astral Sea')
    logging.info(f'Add {member.display_name} to {role}')
    await member.add_roles(role)

    # Saving the below because I think I want to implement this functionality
    # elsewhere, but I do not yet have that spot created so I want to use
    # this as a reminder
    # await member.create_dm()
    # await member.dm_channel.send('welcome message')


@client.event
async def on_error(event, *args, **kwargs):
    trace = sys.exc_info()[2]
    if event == 'on_message':
        logging.error(f'Unhandled message: {args[0]}\n{trace}')
    else:
        raise


def main():
    client.run(token)


if __name__ == '__main__':
    main()
