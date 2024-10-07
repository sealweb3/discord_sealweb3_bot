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
    print(f'{bot.user} start sesión!')

@bot.command()
@commands.has_role('Admin')  # Solo los usuarios con el rol 'Admin' pueden ejecutar este comando
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

# Comando para mostrar el botón de registro
@bot.command()
async def register(ctx):
    global event_active, event_end_time
    if not event_active:
        await ctx.send("No event has been created yet. Use !sealEvent first.")
        return

    if datetime.now() > event_end_time:
        event_active = False
        await ctx.send("The event has ended.")
        return

    await ctx.send("Press button for register in the event.", view=RegistroButtonView())

class RegistroModal(discord.ui.Modal, title="Registro del Evento"):
    
    secretWord = discord.ui.TextInput(
        label="Secret Word",
        style=discord.TextStyle.short,
        placeholder="Insert your secret Word",
        required=True,
        max_length=100
    )

    mail = discord.ui.TextInput(
        label="Mail",
        style=discord.TextStyle.short,
        placeholder="Insert your mail",
        required=True,
        max_length=100
    )
    
    wallet = discord.ui.TextInput(
        label="Wallet by NFT",
        style=discord.TextStyle.short,
        placeholder="Insert your wallet wallet",
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):

        if self.secretWord.value != secret_word:
            await interaction.response.send_message(f"Incorrect or no secret word provided.")
            return
        
        user_data = {
            "name": interaction.user.display_name,
            "id": str(interaction.user.id),
            "email": self.mail.value,
            "wallet": self.wallet.value.lower()
        }

        # Guardar los datos en users.json
        try:
            with open('users.json', 'r+') as json_file:
                data = json.load(json_file)
                data.append(user_data)
                json_file.seek(0)
                json.dump(data, json_file, indent=4)
        except FileNotFoundError:
            with open('users.json', 'w') as json_file:
                json.dump([user_data], json_file, indent=4)

        await interaction.response.send_message(f"¡Thanks {interaction.user.name}! user registered successfully.")

# Clase para el botón
class RegistroButtonView(discord.ui.View):
    @discord.ui.button(label="Register in the event", style=discord.ButtonStyle.green)
    async def registrar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Abrir la ventana modal cuando se presiona el botón
        await interaction.response.send_modal(RegistroModal())

# Iniciar el bot
bot.run(DISCORD_TOKEN)

