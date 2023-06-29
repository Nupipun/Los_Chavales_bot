from PIL import ImageFont, Image, ImageDraw
from io import BytesIO


def create_welcome_card(user_name, avatar):
    font = ImageFont.truetype(r"fonts/ReemKufi-Regular.ttf", 70)
    background_img = Image.open("images/fondo discord.png")
    avatar = Image.open(avatar)
    avatar = avatar.convert("RGBA")

    factor_escala = min(
        background_img.width / avatar.width,
        background_img.height / avatar.height
    )

    new_size = (
        int(avatar.width * factor_escala * 0.45),
        int(avatar.height * factor_escala * 0.45)
    )
    test_img = avatar.resize(new_size)

    result = Image.new("RGBA", background_img.size)

    cx = (background_img.width - test_img.width) // 2
    cy = (background_img.height - test_img.height) // 2

    result.paste(test_img, (cx, cy), mask=test_img)

    result.paste(background_img, (0, 0), mask=background_img)

    draw = ImageDraw.Draw(result)
    text = f"Welcome {user_name}!"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (result.width - text_width) // 2
    text_y = 0
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))

    image_buffer = BytesIO()
    result.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    return image_buffer


if __name__ == "__main__":
    create_welcome_card("Test", "discordpfp.png")
