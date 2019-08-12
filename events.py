import asyncio
import json
import random

import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps
from discord.ext import commands

recent_users = []


async def add_xp(message):
    try:
        with open("userdata.json", "r") as fp:
            data = json.load(fp)
    except FileNotFoundError:
        with open("userdata.json", "w+") as fp:
            data = {f"{message.author.id}": {}}
        data[f"{message.author.id}"]["level"] = 1
        data[f"{message.author.id}"]["xp"] = 0
    try:
        m = data[f"{message.author.id}"]
    except KeyError:
        data[f"{message.author.id}"] = {"level": 1, "xp": 0}
    if data[f"{message.author.id}"]["level"] < 20:
        try:
            data[f"{message.author.id}"]["xp"] += 10
            if data[f"{message.author.id}"]["xp"] >= int(data[f"{message.author.id}"]["level"]) * 100:
                with open("serverdata.json", "r") as fp:
                    _data = json.load(fp)
                level = data[f"{message.author.id}"]["level"] + 1
                role = None
                for r in _data["ranks"].keys():
                    if _data["ranks"][r]["lower"] <= level:
                        role = discord.utils.get(message.guild.roles, id=int(r))
                        await message.author.add_roles(role)
                        role = f"Rank: {role.name}"
                        break
                if not role:
                    role = "You don't have a rank."
                data[f"{message.author.id}"]["xp"] -= int(data[f"{message.author.id}"]["level"]) * 100
                level = data[f"{message.author.id}"]["level"]
                xp = data[f"{message.author.id}"]["xp"]
                await message.author.send(f"Ding! {message.author.mention}, you just advanced to **level {level+1}**! {role}")#f":arrow_double_up: __LEVEL UP__ :arrow_double_up:\n\u200b\n"
                                           #f"{message.author.mention}, you just leveled up to **Level {level+1}**!\n"
                                           #f":sparkles: Level progress: **{xp}/{(level+1)*100}**\n"
                                           #f":chart_with_upwards_trend: Rank: {role}")
                data[f"{message.author.id}"]["level"] += 1
        except KeyError:
            data[f"{message.author.id}"] = {"level": 1, "xp": 0}
            data[f"{message.author.id}"]["xp"] += 10
        with open("userdata.json", "w+") as fp:
            json.dump(data, fp, sort_keys=True, indent=4)


class Handler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.CheckFailure):
            content = "You don't have permission to do that."
        else:
            content = error
        await ctx.send(f":x: {content}")

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before_emojis, after_emojis):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        new_emojis = list(set(before_emojis) ^ set(after_emojis))
        for emoji in new_emojis:
            if str(emoji.id) in data["role_emojis"].keys():
                del data["role_emojis"][str(emoji.id)]
                with open("serverdata.json", "w+") as fp:
                    json.dump(data, fp, sort_keys=True, indent=4)
                break

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        for count, (emoji_id, role_id) in enumerate(data["role_emojis"].items(), 0):
            if role.id == role_id:
                del data["role_emojis"][emoji_id]
                with open("serverdata.json", "w+") as fp:
                    json.dump(data, fp, sort_keys=True, indent=4)
                break
        for rank in data["ranks"].keys():
            if role.id == int(rank):
                del data["ranks"][rank]
                with open("serverdata.json", "w+") as fp:
                    json.dump(data, fp, sort_keys=True, indent=4)
                break

    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        channel = discord.utils.get(member.guild.text_channels, id=data["welcome_channel"])
        text = f"Welcome {member.name}#{member.discriminator} to Speakeasy!"
        background = Image.open("background.png")
        await member.avatar_url.save("profile_picture.png")
        profile_picture = Image.open("profile_picture.png")
        _border = Image.open("pfp_border.png")
        draw = ImageDraw.Draw(background)
        width, height = background.size

        fontsize = 1
        font = ImageFont.truetype("BOOKOSB.TTF", fontsize)

        fraction = 0.93

        while font.getsize(text)[0] < fraction * background.size[0]:
            fontsize += 1
            font = ImageFont.truetype("BOOKOSB.TTF", fontsize)

        t_w, t_h = draw.textsize(text=text, font=font)
        x = int(round((width - t_w) / 2))
        y = int(round((height - t_h) / 2)) + 10
        draw.text((x + 2, y), text, (0, 0, 0), font=font)
        draw.text((x - 2, y), text, (0, 0, 0), font=font)
        draw.text((x, y + 2), text, (0, 0, 0), font=font)
        draw.text((x, y - 2), text, (0, 0, 0), font=font)
        draw.text((x + 1, y - 1), text, (0, 0, 0), font=font)
        draw.text((x - 1, y + 1), text, (0, 0, 0), font=font)
        draw.text((x + 1, y + 1), text, (0, 0, 0), font=font)
        draw.text((x - 1, y - 1), text, (0, 0, 0), font=font)
        draw.text((x, y), text, (255, 255, 255), font=font)

        profile_picture.thumbnail((96, 96), Image.ANTIALIAS)

        mask = Image.new("L", (96, 96), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0) + (96, 96), fill=255)

        output = ImageOps.fit(profile_picture, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)

        px = int(round(width / 2))
        py = int(round(height / 2))
        background.paste(output, (px - 48, int(round(py / 2)) - 60), output)
        background.paste(_border, (px - 49, int(round(py / 2)) - 61), _border)
        background.save('final_image.png')
        file = discord.File(fp="final_image.png")
        await channel.send(file=file)

    @commands.Cog.listener()
    async def on_message(self, message):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        if message.guild and not message.author.bot and message.author.id not in recent_users and not message.content.startswith(data["prefix"]):
            await add_xp(message)
            recent_users.append(message.author.id)
            await asyncio.sleep(random.randint(40, 60))
            recent_users.remove(message.author.id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        if payload.message_id == data["message"]:
            if str(payload.emoji) == "✅":
                guild = self.bot.get_guild(payload.guild_id)
                user = discord.utils.get(guild.members, id=payload.user_id)
                role = discord.utils.get(guild.roles, id=data["member_role"])
                channel = discord.utils.get(guild.text_channels, id=payload.channel_id)
                message = await channel.fetch_message(data["message"])
                print(".")
                await user.add_roles(role)
                await message.remove_reaction("✅", user)
        if payload.channel_id == data["role_channel"]:
            guild = self.bot.get_guild(payload.guild_id)
            user = discord.utils.get(guild.members, id=payload.user_id)
            if payload.emoji.id:
                reacted_role = discord.utils.get(guild.roles, id=data["role_emojis"][f"{payload.emoji.id}"])
                for group in data["me"].keys():
                    if reacted_role.id in data["me"][group]:
                        for role_id in data["me"][group]:
                            role = discord.utils.get(guild.roles, id=role_id)
                            await user.remove_roles(role)
                role = discord.utils.get(guild.roles, id=data["role_emojis"][f"{payload.emoji.id}"])
                await user.add_roles(role)
            else:
                reacted_role = discord.utils.get(guild.roles, id=data["role_emojis"][f"{payload.emoji}"])
                for group in data["me"].keys():
                    if reacted_role.id in data["me"][group]:
                        for role_id in data["me"][group]:
                            role = discord.utils.get(guild.roles, id=role_id)
                            await user.remove_roles(role)
                role = discord.utils.get(guild.roles, id=data["role_emojis"][f"{payload.emoji}"])
                await user.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        if payload.channel_id == data["role_channel"]:
            guild = self.bot.get_guild(payload.guild_id)
            user = discord.utils.get(guild.members, id=payload.user_id)
            if payload.emoji.id:
                reacted_role = discord.utils.get(guild.roles, id=data["role_emojis"][f"{payload.emoji.id}"])
                await user.remove_roles(reacted_role)
            else:
                reacted_role = discord.utils.get(guild.roles, id=data["role_emojis"][f"{payload.emoji}"])
                await user.remove_roles(reacted_role)


def setup(bot):
    bot.add_cog(Handler(bot))
