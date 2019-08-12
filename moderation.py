import json

import discord
from discord.ext import commands


def is_admin(ctx):
    with open("serverdata.json", "r") as fp:
        data = json.load(fp)
    return data["admin_role"] in [role.id for role in ctx.author.roles] or ctx.author.id == 600549104015114270


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["modrole"])
    async def adminrole(self, ctx, role: discord.Role=None):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        if ctx.author.id in [600549104015114270]:
            if role:
                data["admin_role"] = role.id
                with open("serverdata.json", "w+") as fp:
                    json.dump(data, fp, sort_keys=True, indent=4)
                await ctx.send(f":white_check_mark: {role.mention} set as the Administrator role. All users with this role will have permission to use Administrator commands, except this one.")
            else:
                prefix = data["prefix"]
                await ctx.send(f":x: Please enter a role. `{prefix}adminrole <role>`.")
        else:
            await ctx.send(f":no_entry_sign: You don't have permission to execute this command.")

    @commands.check(is_admin)
    @commands.command(aliases=["banuser", "banish"])
    async def ban(self, ctx, user: discord.User, *, reason="Due to an extreme or repeat violation of our rules, you have been banned from the server."):
        await user.send(reason)
        await ctx.guild.ban(user, reason)
        await ctx.send(f":boot: {user.name}#{user.discriminator} has been banned from the server by {ctx.author.name}#{ctx.author.discriminator}.\n\u200b\n"
                       f"**Reason:** {reason}")

    @commands.check(is_admin)
    @commands.command(aliases=["kickuser"])
    async def kick(self, ctx, user: discord.User, *, reason="Due to a violation of the server's rules, you have been kicked from the server."):
        await user.send(reason)
        await ctx.guild.kick(user, reason)
        await ctx.send(f":boot: {user.name}#{user.discriminator} has been kicked from the server by {ctx.author.name}#{ctx.author.discriminator}.\n\u200b\n"
                       f"**Reason:** {reason}")

    @commands.check(is_admin)
    @commands.command(aliases=["setmemberrole"])
    async def memberrole(self, ctx, role: discord.Role):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        data["member_role"] = role.id
        with open("serverdata.json", "w+") as fp:
            json.dump(data, fp, sort_keys=True, indent=4)
        await ctx.send(":white_check_mark: Member role successfully set.")

    @commands.check(is_admin)
    @commands.command(aliases=["muteuser", "silence"])
    async def mute(self, ctx, user: discord.Member, reason="Due to a minor violation of the server's rules, you have been muted."):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role not in user.roles:
            for role in user.roles:
                if role.name != "@everyone":
                    await user.remove_roles(role)
            if not muted_role:
                muted_role = await ctx.guild.create_role(name="Muted", colour=discord.Colour.dark_grey())
            await user.add_roles(muted_role)
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(muted_role, overwrite=overwrite)
            await user.send(reason)
            await ctx.send(f":white_check_mark: **{user.name}** successfully muted.")
        else:
            await ctx.send(f":x: **{user.name}** is already muted.")

    @commands.command(aliases=["aremoverole", "removemodrole", "removearole"])
    async def removeadminrole(self, ctx):
        if ctx.author.id in [600549104015114270]:
            with open("serverdata.json", "r") as fp:
                data = json.load(fp)
            data["admin_role"] = None
            with open("serverdata.json", "w+") as fp:
                json.dump(data, fp, sort_keys=True, indent=4)
            await ctx.send(f":white_check_mark: Administrator role successfully unassigned. Please assign a new one for a specific role to use the Administrator commands.")
        else:
            await ctx.send(f":no_entry_sign: You don't have permission to execute this command.")

    @commands.check(is_admin)
    @commands.command(aliases=["rrc", "removerchan", "removerolechan", "removerolec"])
    async def removerolechannel(self, ctx):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        data["role_channel"] = None
        with open("serverdata.json", "w+") as fp:
            json.dump(data, fp, sort_keys=True, indent=4)
        prefix = data["prefix"]
        await ctx.send(":white_check_mark: Self-assignment role channel removed.\n"
                       f"Set one with `{prefix}rolechannel <channel:optional>`.")

    @commands.check(is_admin)
    @commands.command(aliases=["removewelcomechannel"])
    async def removewelcome(self, ctx):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        data["welcome_channel"] = None
        with open("serverdata.json", "w+") as fp:
            json.dump(data, fp, sort_keys=True, indent=4)
        prefix = data["prefix"]
        await ctx.send(f":white_check_mark: Welcome channel successfully removed. Please set it again with `{prefix}setwelcome <channel:optional>`.")

    @commands.check(is_admin)
    @commands.command(aliases=["rassign", "roleadd", "addrole"])
    async def roleassign(self, ctx, role: discord.Role, emoji, group=None):
        await ctx.send(f"```{emoji}```")
        custom = False
        if group:
            group = group.lower()
        try:
            emoji_obj = discord.utils.get(ctx.guild.emojis, id=int(emoji.split(":")[2].replace(">", "")))
            emoji = emoji_obj.id
            custom = True
        except IndexError:
            custom = False
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        if data["role_channel"]:
            channel = discord.utils.get(ctx.guild.text_channels, id=data["role_channel"])
            data["role_emojis"][f"{emoji}"] = role.id
            if group:
                try:
                    data["me"][group].append(role.id)
                except KeyError:
                    data["me"][group] = []
                    data["me"][group].append(role.id)
            with open("serverdata.json", "w+") as fp:
                json.dump(data, fp, sort_keys=True, indent=4)
            if custom:
                await ctx.send(f":white_check_mark: {role.mention} role set to assign when reacted with {str(emoji_obj)} in {channel.mention}")
            else:
                await ctx.send(f":white_check_mark: {role.mention} role set to assign when reacted with {emoji} in {channel.mention}")
        else:
            prefix = data["prefix"]
            await ctx.send(f":x: You need to have a role assignment channel. See `{prefix}rolechannel <channel:optional>` to set it.")

    @commands.check(is_admin)
    @commands.command(aliases=["roledel", "rolerem", "removerole", "remrole", "delrole"])
    async def roleremove(self, ctx, role: discord.Role):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        if role.id in list(data["role_emojis"].values()):
            if role.id in data["me"]:
                data["me"].remove(role.id)
            for emoji, role_id in data["role_emojis"].items():
                if role_id == role.id:
                    del data["role_emojis"][emoji]
                    break
            for group in data["me"].keys():
                if role.id in data["me"][group]:
                    data["me"][group].remove(role.id)
                    continue
            with open("serverdata.json", "w+") as fp:
                json.dump(data, fp, sort_keys=True, indent=4)
            await ctx.send(f":white_check_mark: {role.mention} successfully removed from the self-assignment roles.")
        else:
            await ctx.send(":x: Unable to remove the role from the self-assignment roles, it isn't bound to any emoji.")

    @commands.check(is_admin)
    @commands.command(aliases=["reactionchannel", "rchannel", "rchan", "rolechan"])
    async def rolechannel(self, ctx, channel: discord.TextChannel=None):
        if channel is None:
            channel = ctx.channel
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        data["role_channel"] = channel.id
        with open("serverdata.json", "w+") as fp:
            json.dump(data, fp, sort_keys=True, indent=4)
        await ctx.send(f":white_check_mark: {channel.mention} successfully set as the self-assignment channel for roles.")

    @commands.command(aliases=["assignmentroles", "aroles", "rolelist"])
    async def roles(self, ctx):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        if data["role_channel"]:
            prefix = data["prefix"]
            roles = data["role_emojis"]
            desc = ""
            for count, (emoji_id, role_id) in enumerate(roles.items(), 0):
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                group = ""
                list(data["me"].keys()).sort()
                for _group in data["me"].keys():
                    if role.id in data["me"][_group]:
                        group = _group.title()
                        break
                try:
                    emoji = discord.utils.get(ctx.guild.emojis, id=int(emoji_id))
                except ValueError:
                    emoji = list(roles.keys())[count]
                if not role:
                    role = f"Unknown Role (deleted?). Please run `{prefix}help rolesetup`."
                if not emoji_id:
                    emoji = f"Unknown Emoji (deleted?). Please run `{prefix}help rolesetup`."
                else:
                    role = role.mention
                    emoji = str(emoji)
                if len(group) == 0:
                    group = "Default"
                desc += f"{emoji} - {role} - {group}\n"
            if len(desc) == 0:
                desc = ":x: No self-assignment roles have been found.\n" \
                       f"Please run `{prefix}role <role> <emoji>`."
            channel = data["role_channel"]
            channel = discord.utils.get(ctx.guild.text_channels, id=channel)
            if channel:
                desc += f"\n\u200b\nRoles available in {channel.mention}."
            else:
                desc += f"\n\u200b\nYou don't have a role channel set. Contact a moderator to set one."
            await ctx.send(desc)
        else:
            prefix = data["prefix"]
            await ctx.send(":x: You don't have a role assignment channel set.\n"
                           f"`{prefix}rolechannel` in a channel of your choice")

    @commands.check(is_admin)
    @commands.command(aliases=["newprefix", "prefix"])
    async def setprefix(self, ctx, prefix="."):
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        if len(prefix) > 5:
            await ctx.send(":x: Please enter a prefix that is a maximum length of 5 characters.")
        else:
            data["prefix"] = prefix
            with open("serverdata.json", "w+") as fp:
                json.dump(data, fp, sort_keys=True, indent=4)
            await ctx.send(f":white_check_mark: **{prefix}** successfully set as the new prefix.")

    @commands.check(is_admin)
    @commands.command(aliases=["setwelcomechannel"])
    async def setwelcome(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        data["welcome_channel"] = channel.id
        with open("serverdata.json", "w+") as fp:
            json.dump(data, fp, sort_keys=True, indent=4)
        await ctx.send(f":white_check_mark: Welcome channel successfully set as {channel.mention}.")

    @commands.check(is_admin)
    @commands.command(aliases=["unsilence"])
    async def unmute(self, ctx, user: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role:
            if muted_role in user.roles:
                await user.remove_roles(muted_role)
                await ctx.send(f":white_check_mark: **{user.name}** successfully unmuted.")
            else:
                await ctx.send(f":x: **{user.name}** isn't currently muted.")
        else:
            await ctx.send(f":x: **{user.name}** cannot be unmuted. Muted role does not exist.")

    @commands.check(is_admin)
    @commands.command(aliases=["entrymsg", "verification"])
    async def verificationmsg(self, ctx, message: discord.Message):
        await message.add_reaction("✅")
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
        data["message"] = message.id
        with open("serverdata.json", "w+") as fp:
            json.dump(data, fp, sort_keys=True, indent=4)


def setup(bot):
    bot.add_cog(Moderation(bot))
