import os
import json
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime, timedelta

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

with open('secret_word.json', 'r') as f:
    secret_word = json.load(f)['secret_word']

event_active = False
event_end_time = None
event_time = 2

@bot.event
async def on_ready():
    print(f'{bot.user} ha iniciado sesión!')

@bot.command()
async def sealEvent(ctx):
    global event_active, event_end_time
    event_active = True
    event_end_time = datetime.now() + timedelta(minutes=event_time)
    await ctx.send(f"Event created. The !seal command will be available for {event_time} minutes.")

@bot.command()
async def seal(ctx):
    global event_active, event_end_time

    if not event_active:
        await ctx.send("No event has been created yet. Use !sealEvent first.")
        return

    if datetime.now() > event_end_time:
        event_active = False
        await ctx.send("The event has ended.")
        return

    if len(ctx.message.content.split()) < 2 or ctx.message.content.split()[1] != secret_word:
        await ctx.send("Incorrect or no secret word provided.")
        return

    user = ctx.author
    email = f"{user.name}@example.com"

    user_data = {
        "name": user.name,
        "id": str(user.id),
        "email": email,
        "wallet": None
    }

    confirm_message = await ctx.send("Please, send your wallet:")

    try:
        message = await bot.wait_for('message', timeout=60.0, check=lambda m: m.author == user and m.channel == ctx.channel)
        if len(message.content.split()) < 1:
            await ctx.send("Wallet not sent.")
            return
        user_data["wallet"] = message.content.split()[0]
    except asyncio.TimeoutError:
        await ctx.send("Time to send wallet has run out.")
        return

    confirm_message = await ctx.send("Please, send your email:")

    try:
        message = await bot.wait_for('message', timeout=60.0, check=lambda m: m.author == user and m.channel == ctx.channel)
        if len(message.content.split()) < 1:
            await ctx.send("Email not sent.")
            return
        user_data["email"] = message.content.split()[0]
    except asyncio.TimeoutError:
        await ctx.send("Time to send email has run out.")
        return

    try:
        with open('users.json', 'r+') as json_file:
            data = json.load(json_file)
            data.append(user_data)
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
    except FileNotFoundError:
        with open('users.json', 'w') as json_file:
            json.dump([user_data], json_file, indent=4)

    await ctx.send(f"{user.name} user registered successfully.")



bot.run(DISCORD_TOKEN)
