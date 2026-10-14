import os
import discord
from discord.ext import commands

# Nastavení práv (intents)
intents = discord.Intents.default()

# Vytvoření instance bota
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} je online a připraven!")
    try:
        # Synchruje slash příkazy s Discordem
        synced = await bot.tree.sync()
        print(f"🔄 Nenačteno/synchováno {len(synced)} slash příkazů.")
    except Exception as e:
        print(f"❌ Chyba při synchronizaci příkazů: {e}")

@bot.tree.command(name="ping", description="Odpoví pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓")

# Načtení tokenu z proměnných prostředí (Environment Variables)
TOKEN = os.getenv("DISCORD_TOKEN")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Chyba: Není nastaven DISCORD_TOKEN v proměnných prostředí!")
