import constants as c
import discord
from card_image_logic import create_welcome_card
from io import BytesIO
import wavelink
from LCMusicEvents import LCMusicEvents
from LCCommands import LCCommands


class LCBot(LCMusicEvents, discord.Client):
    def __init__(self, logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger

    async def on_ready(self):
        self.logger.info(f"Connected as {self.user.name}")
        try:
            self.logger.info("Starting lavalink...")
            await self.start_lavalink()
            node: wavelink.Node = wavelink.Node(uri="http://localhost:2333", password="youshallnotpass")
            await wavelink.NodePool.connect(client=self, nodes=[node])
            self.logger.info("Syncing commands...")
            tree = LCCommands(self)
            synced = await tree.sync()
            self.logger.info(f"Synced {len(synced)} command(s)")
            # self.check_new_video.start()
        except Exception as e:
            self.logger.error(e)

    async def on_member_join(self, member: discord.Member):
        channel = await self.fetch_channel(c.WELCOME_CHANNEL_ID)
        user_id = member.id

        user = await self.fetch_user(user_id)
        avatar_data = BytesIO(await user.display_avatar.read())

        card = create_welcome_card(user, avatar_data)

        file = discord.File(card, filename="welcome_card.png")
        msg = f"Hello {member} welcome to Los Chavales!\n\nHola {member} bienvenido a Los Chavales!"

        await channel.send(msg, file=file)

    async def on_interaction(self, interaction: discord.Interaction):
        option_list = {}
        if "options" in interaction.data:
            for option in interaction.data["options"]:
                option_list[option["name"]] = option["value"]
        option_str = ", ".join([f"{key}: {value}" for key, value in option_list.items()])
        self.logger.info(f"User: {interaction.user} executed: {interaction.data['name']} args: [{option_str}]")
