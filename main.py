import discord
from bot import LCBot


TOKEN = "MTExMjkzMjgxNDQ2MDA0NzM2MA.GOSzVA.o_spK1IiNOkp--B4a1HSASMlyaSvOwHyTxwJaY"

intents = discord.Intents.all()

client = LCBot(intents=intents)

client.run(TOKEN)
