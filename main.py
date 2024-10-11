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
event_time = 2
locaselect = ''


@bot.event
async def on_ready():
    print(f'{bot.user} start sesión!')

@bot.command()
@commands.has_role('Admin')  # Solo los usuarios con el rol 'Admin' pueden ejecutar este comando
async def sealEvent(ctx):
    await ctx.send("Select location.", view=MySelectMenu())
    

@bot.command()
@commands.has_role('Admin')  # Solo los usuarios con el rol 'Admin' pueden ejecutar este comando
async def attest(ctx):
    await ctx.send("To attest your identity, please visit [sealweb3.com](https://sealweb3.com) and follow the verification process")


@bot.command()
@commands.has_role('Admin')  # Solo los usuarios con el rol 'Admin' pueden ejecutar este comando
async def reset(ctx):
    global event_active
    event_active = False
    
    # Borrar el archivo users.json si existe
    if os.path.exists('users.json'):
        os.remove('users.json')
        await ctx.send("Datos de usuarios y estados reseteados correctamente. El archivo users.json ha sido eliminado.")
    else:
        await ctx.send("No hay datos de usuarios para eliminar.")
    
# Comando para mostrar el botón de registro
@bot.command()
async def register(ctx):
    global event_active, event_end_time
    if not event_active:
        await ctx.send("No event has been created yet. Use !sealEvent first.")
        return

    if datetime.now() > event_end_time:
        event_active = False
        image_active = False
        await ctx.send("The event has ended.")
        return

    await ctx.send("Press button for register in the event.", view=RegistroButtonView())

class RegistroModal(discord.ui.Modal, title="Event register"):
    
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
                event = data[0]
                if "participants" not in event:
                    event["participants"] = []
                event["participants"].append(user_data)

                json_file.seek(0)
                json.dump(data, json_file, indent=4)
                json_file.truncate()  # Asegurar que se borre contenido anterior que no se use

        except FileNotFoundError:
            await interaction.response.send_message("Error: No se encontró el archivo de eventos.", ephemeral=True)
            return

        await interaction.response.send_message(f"¡Thanks {interaction.user.name}! user registered successfully.")

# Class for button
class RegistroButtonView(discord.ui.View):
    @discord.ui.button(label="Register in the event", style=discord.ButtonStyle.green)
    async def registrar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Abrir la ventana modal cuando se presiona el botón
        if event_active:
            await interaction.response.send_modal(RegistroModal())

class EventButtonView(discord.ui.View):
    @discord.ui.button(label="Create event", style=discord.ButtonStyle.green)
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Abrir la ventana modal cuando se presiona el botón
        if not event_active:
            await interaction.response.send_modal(CreateEventModal())

class MySelectMenu(discord.ui.View):
    @discord.ui.select(placeholder="location", min_values=1, max_values=1, options=[
        discord.SelectOption(label="Online", description="Event online"),
        discord.SelectOption(label="In person", description="Event in person"),
        discord.SelectOption(label="Mixed", description="Event will be onlina and in person")
    ])
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        locaselect = select.values[0]
        await interaction.response.send_message("Is neccesary push in create event", view=EventButtonView())


# Class for modal create event

class CreateEventModal(discord.ui.Modal, title="Create event"):

    name = discord.ui.TextInput(
        label="Event name",
        style=discord.TextStyle.short,
        placeholder="Insert name event",
        required=True,
        max_length=100
    )

    description = discord.ui.TextInput(
        label="Event description",
        style=discord.TextStyle.long,
        placeholder="Description the event",
        required=True
    )

    event_link = discord.ui.TextInput(
        label="Event Link",
        style=discord.TextStyle.short,
        placeholder="Event Link",
        required=True
    )

    partners = discord.ui.TextInput(
        label="partners (separated by commas)",
        style=discord.TextStyle.short,
        placeholder="partners by event",
        required=False
    )

    image = discord.ui.TextInput(
        label="Image link",
        style=discord.TextStyle.short,
        placeholder="Image link",
        required=True,
    )
    

    async def on_submit(self, interaction: discord.Interaction):
        global event_end_time, event_time, event_active
        global locaselect
        event_data = {
            "name": self.name.value,
            "description": self.description.value,
            "date": str(datetime.now()),
            "location": locaselect,
            "partners": self.partners.value.split(",") if self.partners.value else [],
            "event_link": self.event_link.value,
            "linked_attestation_id": "quemado",
            "imagen": self.image.value,
        }
        try:
            with open('users.json', 'r+') as json_file:
                data = json.load(json_file)
                data.append(event_data)
                json_file.seek(0)
                json.dump(data, json_file, indent=4)
        except FileNotFoundError:
            with open('users.json', 'w') as json_file:
                json.dump([event_data], json_file, indent=4)

        event_active = True
        event_end_time = datetime.now() + timedelta(minutes=event_time)
        await interaction.response.send_message(f"Event create.")

# Iniciar el bot
bot.run(DISCORD_TOKEN)

