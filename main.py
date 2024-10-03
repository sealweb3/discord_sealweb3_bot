import os
import json
import discord
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

@bot.event
async def on_ready():
    print(f'{bot.user} ha iniciado sesión!')

@bot.command()
async def sealEvent(ctx):
    global event_active, event_end_time
    event_active = True
    event_end_time = datetime.now() + timedelta(minutes=60)
    await ctx.send("Evento creado. El comando !seal estará disponible por 60 minutos.")

@bot.command()
async def seal(ctx, *args):
    global event_active, event_end_time

    if not event_active:
        await ctx.send("No se ha creado el evento. Usa !sealEvent primero.")
        return

    if datetime.now() > event_end_time:
        event_active = False
        await ctx.send("El evento ha terminado.")
        return

    if len(args) == 0 or args[0] != secret_word:
        await ctx.send("Palabra secreta incorrecta o no proporcionada.")
        return

    user = ctx.author
    email = f"{user.name}@example.com"

    user_data = {
        "name": user.name,
        "id": str(user.id),
        "email": email
    }

    try:
        with open('users.json', 'r+') as f:
            data = json.load(f)
            data.append(user_data)
            f.seek(0)
            json.dump(data, f, indent=4)
    except FileNotFoundError:
        with open('users.json', 'w') as f:
            json.dump([user_data], f, indent=4)

    await ctx.send(f"Usuario {user.name} registrado correctamente.")

bot.run(DISCORD_TOKEN)
