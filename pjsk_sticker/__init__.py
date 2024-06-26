import asyncio
import base64
import os
from io import BytesIO
from os.path import join
import random

from PIL import Image, ImageDraw, ImageFont

from .chara import check_chara, check_name

PIC_PATH = os.path.dirname(__file__)


async def contain_chinese(check_str):
    try:
        return next((True for ch in check_str if '\u4e00' < ch <= '\u9fa5'), False)
    except Exception as e:
        print("发生了异常：", str(e))
        return False


async def contain_jepanese(check_str):
    try:
        return next((True for ch in check_str if '\u0800' <= ch < '\u4e00'), False)
    except Exception as e:
        print("发生了异常：", str(e))
        return False


async def crop_transparent(image):
    try:
        width, height = image.size
        pixels = list(image.getdata())
        left = width
        right = 0
        top = height
        bottom = 0
        for y in range(top):
            for x in range(width):
                pixel = pixels[y * width + x]
                alpha = pixel[3]
                if alpha != 0:
                    left = min(left, x)
                    right = max(right, x)
                    top = min(top, y)
                    bottom = max(bottom, y)
        return image.crop((left, top, right, bottom))
    except Exception as e:
        print("发生了异常：", str(e))
        return None


async def stickmaker(image, x: int, y: int, text: str, angle: int, size: int, fill: tuple):
    try:
        border = 5
        space = -7
        size -= 3
        angle -= 3
        if await contain_jepanese(text):
            font = ImageFont.truetype(join(PIC_PATH, 'fonts', 'stick.ttf'), size)
        elif await contain_chinese(text):
            font = ImageFont.truetype(join(PIC_PATH, 'fonts', 'stick2.ttf'), size)
        else:
            font = ImageFont.truetype(join(PIC_PATH, 'fonts', 'stick.ttf'), size)
        none_img = Image.new("RGBA", (500, 500), (255, 255, 255, 0))
        m1 = 250 - int(image.size[0] / 2)
        n1 = 250 - int(image.size[1] / 2)
        none_img.paste(image, (m1, n1))
        text_img = Image.new("RGBA", none_img.size, (255, 255, 255, 0))
        a1, b1 = none_img.size

        lines = text.split("\n")
        for i, line in enumerate(lines):
            try:
                width, _ = ImageDraw.Draw(text_img).textsize(line, font=font)
            except:
                width = ImageDraw.Draw(text_img).textlength(line, font=font)
            text_x = (a1 - width) / 2
            text_y = int(b1 / 2) - 2 * border + (i - (len(lines) - 1) / 2) * (size + space)

            text_draw = ImageDraw.Draw(text_img)
            text_draw.text((text_x, text_y), line, font=font, stroke_width=border, stroke_fill=(255, 255, 255),
                           spacing=space)
            text_draw.text((text_x, text_y), line, font=font, fill=fill, spacing=space + 10)

        rotated_text = text_img.rotate(angle, Image.BICUBIC, expand=True)
        a2, b2 = rotated_text.size
        line = len(lines)
        none_img.paste(rotated_text, (
            (int(x - 0.5 * a2) - 2 * (2 - line) * border + m1), int(y - 0.5 * b2 - 2 * (2 - line) * border + n1)),
                       rotated_text)
        return image if (image := await crop_transparent(none_img)) else None
    except Exception as e:
        print("发生了异常：", str(e))
        return None


async def stick_maker(chara: str, text: str):
    try:
        if not (chara_name := await check_chara(chara)):
            return f"角色{chara}不存在"
        choices = [i for i in range(1, 16) if i % 5 != 0]
        chara_id = random.choice(choices)
        chara_id = f"0{str(chara_id)}" if 0 < chara_id <= 9 else str(chara_id)
        name = f'{chara_name} {chara_id}'
        if not (info := await check_name(name)):
            return "id不存在,请用[贴纸预览 角色名]查看对应贴纸"
        path = join(join(PIC_PATH, 'img'), info["img"])
        image = Image.open(path)
        default = info["defaultText"]
        size = default["s"]
        hex_color = info["color"]
        rgb_color = tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
        text = await split_text_into_lines(text, max_chars_per_line=5)
        if img := await stickmaker(image, x=default["x"], y=default["y"], text=text, angle=-6 * default["r"], size=size,
                                   fill=rgb_color):
            buf = BytesIO()
            img = img.convert('RGBA')
            img.save(buf, format='GIF')
            # base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
            return f'[CQ:image,file=base64://{base64.b64encode(buf.getvalue()).decode()}]{chara_name}_{chara_id}  '
        else:
            return "贴纸生成失败"
    except Exception as e:
        print("发生了异常：", str(e))
        return "贴纸生成失败"


async def maker(chara: str, chara_id: str, text: str):
    try:
        if not (chara_name := await check_chara(chara)):
            return f"角色{chara}不存在"
        chara_id = f"0{str(chara_id)}" if 0 < chara_id <= 9 else str(chara_id)
        name = f'{chara_name} {chara_id}'
        if not (info := await check_name(name)):
            return "id不存在,请用[贴纸预览 角色名]查看对应贴纸"
        path = join(join(PIC_PATH, 'img'), info["img"])
        image = Image.open(path)
        default = info["defaultText"]
        size = default["s"]
        hex_color = info["color"]
        rgb_color = tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
        text = await split_text_into_lines(text, max_chars_per_line=5)
        if img := await stickmaker(image, x=default["x"], y=default["y"], text=text, angle=-6 * default["r"], size=size,
                                   fill=rgb_color):
            buf = BytesIO()
            img = img.convert('RGBA')
            img.save(buf, format='GIF')
            # base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
            return f'[CQ:image,file=base64://{base64.b64encode(buf.getvalue()).decode()}]'
        else:
            return "贴纸生成失败"
    except Exception as e:
        print("发生了异常：", str(e))
        return "贴纸生成失败"

async def random_stick(text: str):
    try:
        # info0 = [x for x in info if x]
        random_chara = random.randint(1, 26)
        choices = [i for i in range(1, 16) if i % 5 != 0]
        while True:
            chara_id = random.choice(choices)
            chara_id = f"0{str(chara_id)}" if 0 < chara_id <= 9 else str(chara_id)
            if chara_name := await check_chara(f"{random_chara}"):
                name = f'{chara_name} {chara_id}'
                await asyncio.sleep(1)
                if await check_name(name):
                    break
            else:
                return await f"角色{random_chara}不存在"
        # return stick_maker(str(random_chara), chara_id, text)
        name = f'{chara_name} {chara_id}'
        info = await check_name(name)
        path = join(join(PIC_PATH, 'img'), info["img"])
        image = Image.open(path)
        default = info["defaultText"]
        size = default["s"]
        hex_color = info["color"]
        rgb_color = tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
        text = await split_text_into_lines(text, max_chars_per_line=5)
        if img := await stickmaker(image, x=default["x"], y=default["y"], text=text, angle=-6 * default["r"], size=size,
                                   fill=rgb_color):
            buf = BytesIO()
            img = img.convert('RGBA')
            img.save(buf, format='GIF')
            # base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
            return f'[CQ:image,file=base64://{base64.b64encode(buf.getvalue()).decode()}]{chara_name}_{chara_id}  '
        else:
            return "贴纸生成失败"
    except Exception as e:
        print("发生了异常：", str(e))
        return

async def split_text_into_lines(text, max_chars_per_line):
    if len(text) < max_chars_per_line:
        return text

    mid = len(text) // 2
    first_line = text[:mid]
    second_line = text[mid:]

    return first_line + '\n' + second_line

