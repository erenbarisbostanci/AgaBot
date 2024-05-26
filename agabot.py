import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent

load_dotenv() 

token = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command(name='SA')
async def ping(ctx):
    await ctx.send('AS')

@bot.command(name='sa')
async def ping(ctx):
    await ctx.send('as')

queue = []

async def play_next(ctx):
    if len(queue) > 0:
        url = queue.pop(0)
        await play_url(ctx, url)

async def play_url(ctx, url):
    channel = ctx.author.voice.channel
    
    try:
        voice_client = await channel.connect()
    except discord.ClientException:
        voice_client = ctx.voice_client

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
            print(f'Downloaded file: {filename}')
            audio_source = discord.FFmpegPCMAudio(source=filename)

            def after_playing(error):
                if error:
                    print(f'Error during playback: {error}')
                if os.path.exists(filename):
                    os.remove(filename)
                    print(f'Removed file: {filename}')
                asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)

            if not voice_client.is_playing():
                print('Starting playback')
                voice_client.play(audio_source, after=after_playing)
            else:
                queue.append(url)
                await ctx.send("Added to queue.")
                
    except Exception as e:
        print(f'An error occurred: {e}')
        await ctx.send(f'An error occurred: {e}')
        await voice_client.disconnect()

@bot.command(name='çal', help='Plays an MP3 file in the voice channel')
async def play(ctx, url: str):
    if not ctx.author.voice:
        await ctx.send("Ses kanalına bağlı değilsin.")
        return
    
    queue.append(url)
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        await play_next(ctx)


bot.run(token)