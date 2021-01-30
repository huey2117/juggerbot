import os
import sys
from dotenv import load_dotenv
import logging
from datetime import date, timedelta
import discord
from discord.ext import commands
import youtube_dl
import ffmpeg


logging.basicConfig(
    filename='jbot.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
target_guild = os.getenv('DISCORD_GUILD')

# Presences and Members are required additional permissions
# ex. members is needed for the on_member_join() event to be registered
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.reactions = True

# Initialize bot
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
    logging.info(f'Adding {member.display_name} to {role}')
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


@client.event
async def on_raw_reaction_add(payload):
    reaction = payload.emoji
    user = await client.fetch_user(payload.user_id)
    channel = await client.fetch_channel(payload.channel_id)

    member = payload.member
    # This section handles the welcome role add reactions
    welcome_id = discord.utils.get(member.guild.channels, name="welcome")
    if channel == welcome_id:
        logging.info(f"{user.name} reacted to welcome message")

        # Create key value pairs of reaction id and role name pairs
        reaction_to_role = {}
        role_reactions = ['wow', 'd20', 'mtg', 'sus', 'press_F']
        role_names = ['WoW', 'Tabletop', 'MtG', 'sus AF', 'Commoner']
        for react, rname in zip(role_reactions, role_names):
            for e in client.emojis:
                if e.name == react:
                    reaction_id = client.get_emoji(e.id)
                    reaction_to_role[reaction_id.id] = discord.utils.get(
                        member.guild.roles,
                        name=rname
                    )
        if reaction.id in reaction_to_role:
            role = reaction_to_role[reaction.id]
            if role in member.roles:
                logging.info(f"Not adding {user.name} to {role} "
                             f"as they are already a member."
                             )
            else:
                logging.info(f"Adding {user.name} to {role}")
                await member.add_roles(role)


@client.event
async def on_raw_reaction_remove(payload):
    reaction = payload.emoji
    user = await client.fetch_user(payload.user_id)
    channel = await client.fetch_channel(payload.channel_id)

    # The remove action often comes without a payload, so I will attempt
    # to grab the member object from the user id.
    # get_all_members() returns a list, so I need the 0th element since
    # only one member should match a specific action
    member = payload.member or (
        [m
         for m in client.get_all_members()
         if m.id == user.id
         ][0]
    )
    # This section handles the welcome role removal reactions
    welcome_id = discord.utils.get(member.guild.channels, name="welcome")
    if channel == welcome_id:
        logging.info(f"{user.name} removed a reaction to welcome message")

        # Create key value pairs of reaction id and role name pairs
        reaction_to_role = {}
        role_reactions = ['wow', 'd20', 'mtg', 'sus', 'press_F']
        role_names = ['WoW', 'Tabletop', 'MtG', 'sus AF', 'Commoner']
        for react, rname in zip(role_reactions, role_names):
            for e in client.emojis:
                if e.name == react:
                    reaction_id = client.get_emoji(e.id)
                    reaction_to_role[reaction_id.id] = discord.utils.get(
                        member.guild.roles,
                        name=rname
                    )
        if reaction.id in reaction_to_role:
            role = reaction_to_role[reaction.id]
            if role in member.roles:
                logging.info(f"Removing {user.name} from {role}")
                await member.remove_roles(role)
            else:
                logging.info(f"Not removing {user.name} from {role} "
                             f"as they are not a member."
                             )

@client.command()
async def psl(ctx):
    x = date.today() - date(2020, 8, 15)
    await ctx.send(str(x.days) + " until the Pumpkin Spice Latte returns! Get ready!")

@client.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Music Section
@client.command()
async def play(ctx, url: str):
    song = os.path.isfile("song.mp3")
    try:
        if song:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the "
                       "'!stop' command")
        return

    # Connect to the voice channel the user is in or to the General channel
    # if the user is not yet in a voice channel
    try:
        user_channel = ctx.message.author.voice.channel
        voice_channel = discord.utils.get(
            ctx.guild.voice_channels,
            id=user_channel
        )
    except AttributeError:
        voice_channel = discord.utils.get(
            ctx.guild.voice_channels,
            name='General / Among Us'
        )
    await voice_channel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    yt_options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
    }
    with youtube_dl.YoutubeDL(yt_options) as ydl:
        ydl.download([url])
    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            os.rename(file, 'song.mp3')
    voice.play(discord.FFmpegPCMAudio('song.mp3'))


@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send('The bot is not connected to a voice channel')


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send('Currently no audio is playing.')


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_puased():
        voice.resume()
    else:
        await ctx.send('Audio is not paused.')


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


def main():
    client.run(token)


if __name__ == '__main__':
    main()
