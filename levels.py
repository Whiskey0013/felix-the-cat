import json

import discord
from discord.ext import commands


def is_admin(ctx):
    with open("serverdata.json", "r") as fp:
        data = json.load(fp)
    return data["admin_role"] in [role.id for role in ctx.author.roles] or ctx.author.id == 600549104015114270


class Levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["profile"])
    async def level(self, ctx, user: discord.User=None):
        if user is None:
            user = ctx.author
        with open("userdata.json", "r") as fp:
            data = json.load(fp)
        level = data[f"{user.id}"]["level"]
        xp = data[f"{user.id}"]["xp"]
        with open("serverdata.json", "r") as fp:
            _data = json.load(fp)
        role = None
        for r in _data["ranks"].keys():
            if _data["ranks"][r]["lower"] <= level <= _data["ranks"][r]["upper"]:
                role = discord.utils.get(ctx.guild.roles, id=int(r))
                role = f"{role.mention}"
                break
        if not role:
            role = "You don't have a rank."
        await ctx.send(f":clipboard: __{user.display_name}'s Profile__ :clipboard:\n\u200b\n"
                       f"**Level**: {level}\n"
                       f"**XP**: {xp}/{level*100}\n"
                       f"**Rank**: {role}")

    @commands.check(is_admin)
    @commands.command(aliases=["ra", "radd", "addrank"])
    async def rankadd(self, ctx, role: discord.Role, start_level: int, end_level: int):
        start_level = abs(start_level)
        end_level = abs(end_level)
        with open("serverdata.json") as fp:
            data = json.load(fp)
        if int(start_level) < int(end_level):
            enable = True
            coll_rank = None
            for rank in data["ranks"].keys():
                if (data["ranks"][rank]["lower"] <= start_level <= data["ranks"][rank]["upper"]
                ) or (data["ranks"][rank]["lower"] <= end_level <= data["ranks"][rank]["upper"]
                ) or (start_level <= data["ranks"][rank]["lower"] <= end_level
                ) or (start_level <= data["ranks"][rank]["upper"] <= end_level):

                    enable = False
                    coll_rank = discord.utils.get(ctx.guild.roles, id=int(rank))
                    break
            if enable:
                data["ranks"][str(role.id)] = {"lower": int(start_level), "upper": int(end_level)}
                with open("serverdata.json", "w+") as fp:
                    json.dump(data, fp, sort_keys=True, indent=4)
                msg = f":white_check_mark: Successfully set {role.mention} as the rank for levels **{start_level}**-**{end_level}**."
            else:
                prefix = data["prefix"]
                msg = f":x: Couldn't add this rank as the starting and ending levels overlap or clash with another rank's levels ({coll_rank.mention}).\n" \
                      f"Please see `{prefix}ranks`."
            await ctx.send(msg)
        else:
            prefix = data["prefix"]
            await ctx.send(f":x: Please make sure that the final level for the rank is higher than the starting level.\n"
                           f"Please see `{prefix}rankadd <role> <from level> <to level>`.")

    @commands.check(is_admin)
    @commands.command(aliases=["rankdel", "rankremove", "delrank", "removerank"])
    async def rankdelete(self, ctx, role: discord.Role):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        prefix = data["prefix"]
        message = ""
        for r in data["ranks"].keys():
            if str(role.id) in r:
                lower = data["ranks"][r]["lower"]
                upper = data["ranks"][r]["upper"]
                del data["ranks"][r]
                with open("serverdata.json", "w+") as fp:
                    json.dump(data, fp, sort_keys=True, indent=4)
                message = f":white_check_mark: Rank successfully removed. Levels **{lower}** to **{upper}** no longer have a rank assigned to them.\n" \
                          f"Please see `{prefix}rankadd <role> <from level> <to level>` to add a rank to these levels."
                break
        if len(message) == 0:
            message = ":x: No ranks were found.\n" \
                      f"Please see `{prefix}rankadd <role> <from level> <to level>` to add some level ranks."
        await ctx.send(message)

    @commands.command(aliases=["roleranks", "rankroles", "levelranks", "levelroles", "levels"])
    async def ranks(self, ctx):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        ranks = ""
        lower_list = []
        for rank in data["ranks"].keys():
            lower_list.append(data["ranks"][rank]["lower"])
        lower_list.sort()
        count = 0
        while count != len(lower_list):
            for r in data["ranks"].keys():
                role = discord.utils.get(ctx.guild.roles, id=int(r))
                lower = data["ranks"][r]["lower"]
                upper = data["ranks"][r]["upper"]
                if lower == lower_list[count]:
                    ranks += f"{role.mention} - Levels **{lower}** to **{upper}**\n"
                    count += 1
                    if count == len(lower_list):
                        break
        if len(ranks) == 0:
            prefix = data["prefix"]
            ranks = f"Sorry, you don't have any level ranks set.\nPlease see `{prefix}rankadd <role> <from level> <to level>`."
        await ctx.send(f":beginner: __Level Ranks__ :beginner:\n\u200b\n"
                       f"{ranks}")


def setup(bot):
    bot.add_cog(Levels(bot))
