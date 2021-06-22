import discord
from discord.ext import commands
from sheets import SheetReader

sr = SheetReader()
intents = discord.Intents().default()
intents.guilds = True
intents.messages = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.load_extension("events")
bot.run(sr.config.get("discordToken"))
