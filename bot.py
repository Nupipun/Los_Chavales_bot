from discord.app_commands import CommandTree
import discord


class LCCommands(CommandTree):
    def __init__(self, client):
        super().__init__(client)

        @self.command(name="ping")
        async def ping(interaction: discord.Interaction):
            await interaction.response.send_message("Pong!")


class LCBot(discord.Client):
    async def on_ready(self):
        print(f"{self.user.name} is working.")
        try:
            print("Syncing commands...")
            tree = LCCommands(self)
            synced = await tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

    async def on_interaction(self, interaction: discord.Interaction):
        print(f"el usuario {interaction.user} ha ejecutado {interaction.data['name']}")
