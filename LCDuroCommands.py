from discord.app_commands import CommandTree
from discord import Interaction, Attachment, File
import os
import random


class LCDuroCommands(CommandTree):
    def __init__(self, client):
        super().__init__(client)
        self.duro_images = []
        self.gato_images = []
        self.borzois_images = []
        self.lmao_images = []

        @self.command(name="durosave")
        async def durosave(interaction: Interaction, imagen: Attachment):
            path = os.path.join("images", "duro_images")
            if not os.path.exists(path):
                os.mkdir(path)

            await imagen.save(os.path.join(path, imagen.filename))
            await interaction.response.send_message("Imagen dura guardada.", ephemeral=True)

        @self.command(name="gatosave")
        async def gatosave(interaction: Interaction, imagen: Attachment):
            path = os.path.join("images", "gato_images")
            if not os.path.exists(path):
                os.mkdir(path)

            await imagen.save(os.path.join(path, imagen.filename))
            await interaction.response.send_message("Imagen MEOW guardada.", ephemeral=True)

        @self.command(name="duro")
        async def duro(interaction: Interaction):
            images = self.obtener_imagenes("duro")
            if not images:
                await interaction.response.send_message("No hay imágenes disponibles.", ephemeral=True)
                return
            picture = self.cargar_duro_images(images)
            await interaction.response.send_message(file=picture)

        @self.command(name="gato")
        async def gato(interaction: Interaction):
            images = self.obtener_imagenes("gato")
            if not images:
                await interaction.response.send_message("No hay imágenes disponibles.", ephemeral=True)
                return
            picture = self.cargar_gato_images(images)
            await interaction.response.send_message(file=picture)

        @self.command(name="borzoisave")
        async def borzoisave(interaction: Interaction, imagen: Attachment):
            path = os.path.join("images", "borzoi_images")
            if not os.path.exists(path):
                os.mkdir(path)
            await imagen.save(path, imagen.filename)
            await interaction.response.send_message("Imagen de borzoi guardada.", ephemeral=True)

        @self.command(name="borzoi")
        async def borzoi(interaction: Interaction):
            images = self.obtener_imagenes("borzoi")
            if not images:
                await interaction.response.send_message("No hay imágenes disponibles.", ephemeral=True)
                return
            picture = self.cargar_borzoi_images(images)
            await interaction.response.send_message(file=picture)

        @self.command(name="lmaosave")
        async def lmaosave(interaction: Interaction, imagen: Attachment):
            path = os.path.join("images", "lmao_images")
            if not os.path.exists(path):
                os.mkdir(path)
            await imagen.save(path, imagen.filename)
            await interaction.response.send_message("Imagen de lmao guardada.", ephemeral=True)

        @self.command(name="lmao")
        async def lmao(interaction: Interaction):
            images = self.obtener_imagenes("lmao")
            if not images:
                await interaction.response.send_message("No hay imágenes disponibles.", ephemeral=True)
                return
            picture = self.cargar_lmao_images(images)
            await interaction.response.send_message(file=picture)

    def obtener_imagenes(self, image_type):
        path = os.path.join("images", image_type + "_images")
        images = os.listdir(path)
        images = [image for image in images if image not in self.duro_images]
        return images

    def cargar_duro_images(self, images):
        random_image = random.choice(images)
        self.duro_images.append(random_image)
        with open(os.path.join("images", "duro_images", random_image), "rb") as image:
            picture = File(image)
            return picture

    def cargar_gato_images(self, images):
        random_image = random.choice(images)
        self.gato_images.append(random_image)
        with open(os.path.join("images", "gato_images", random_image), "rb") as image:
            picture = File(image)
            return picture

    def cargar_borzoi_images(self, images):
        random_image = random.choice(images)
        self.borzoi_images.append(random_image)
        with open(os.path.join("images", "borzoi_images", random_image), "rb") as image:
            picture = File(image)
            return picture

    def cargar_lmao_images(self, images):
        random_image = random.choice(images)
        self.lmao_images.append(random_image)
        with open(os.path.join("images", "lmao_images", random_image), "rb") as image:
            picture = File(image)
            return picture
