import json
import sys
import traceback

from discord.ext import commands
import discord

print(discord.__file__)



def get_prefix(bot, message):
    try:
        with open("serverdata.json", "r") as fp:
            data = json.load(fp)
    except FileNotFoundError:
        data = {}
        data["admin_role"] = None
        data["me"] = {}
        data["member_role"] = None
        data["message"] = None
        data["prefix"] = "."
        data["ranks"] = {}
        data["role_channel"] = None
        data["role_emojis"] = {}
        data["welcome_channel"] = None
        with open("serverdata.json", "w+") as fp:
            json.dump(data, fp, sort_keys=True, indent=4)
    return data["prefix"]


bot = commands.Bot(command_prefix=get_prefix)
bot.remove_command("help")


@bot.event
async def on_ready():
    print("Whiskey ready for drinkin'.")


@bot.command(aliases=["commands", "cmds", "cmdlist"])
async def help(ctx):
    with open("serverdata.json", "r") as fp:
        data = json.load(fp)
    prefix = data["prefix"]
    general = "\n:arrow_right: General Commands :arrow_left:\n" \
              f"`{prefix}help` - Shows this command.\n\u200b\n" \
              f"`{prefix}level <user:optional>` - Shows the level progress and rank of the specified user. Shows your own level if none is specified.\n\u200b\n" \
              f"`{prefix}ranks` - Shows all the available XP ranks.\n\u200b\n" \
              f"`{prefix}roles` - Shows roles that you can get via self-assigning through emojis.\n\u200b"
    moderator = ""
    owner = ""
    if data["admin_role"] in [role.id for role in ctx.author.roles]:
        moderator = "\n\u200b\n:closed_lock_with_key: Moderator Commands :closed_lock_with_key:\n" \
                    f"`{prefix}ban <user> <reason:optional>` - Bans the user for the specified reason. Default reason is used if none is provided.\n\u200b\n" \
                    f"`{prefix}kick <user> <reason:optional>` - Kicks the user for the specified reason. Default reason is used if none is provided.\n\u200b\n" \
                    f"`{prefix}memberrole <role>` - Sets the role that users receive when they verify themselves.\n\u200b\n" \
                    f"`{prefix}mute <user>` - Mutes the user for a specific reason. Reason is DMed to the user.\n\u200b\n" \
                    f"`{prefix}rankadd <role> <from level> <to level>` - Adds a rank to a user when a specific XP level is reached.\n\u200b\n" \
                    f"`{prefix}rankdelete <role>` - Removes a rank from the XP level list.\n\u200b\n" \
                    f"`{prefix}ranks` - Displays all XP level ranks.\n\u200b\n" \
                    f"`{prefix}removerolechannel` - Removes the role self-assignment channel functionality.\n\u200b\n" \
                    f"`{prefix}removewelcomechannel` - Removes the channel where welcome banners are sent.\n\u200b\n" \
                    f"`{prefix}roleassign <role> <emoji> <group:optional>` - Adds role to the self-assignment roles.\n\u200b\n" \
                    f"`{prefix}roleremove <role>` - Removes a channel from the self-assignment function.\n\u200b\n" \
                    f"`{prefix}rolechannel <channel:optional>` - Sets the self-assignment role channel.\n\u200b\n" \
                    f"`{prefix}roles` - Displays all the available self-assignment roles.\n\u200b\n" \
                    f"`{prefix}setprefix <prefix:optional>` - Sets a new prefix for the bot. Sets as `!` if none is provided.\n\u200b\n" \
                    f"`{prefix}setwelcomechannel <channel:optional>` - Sets the welcome channel where welcome banners are sent to.\n\u200b\n" \
                    f"`{prefix}unmute <user>` - Unmutes a muted user.\n\u200b\n" \
                    f"`{prefix}verification <channel> <message_id>` - Sets the message that users agree to to get access to the rest of the server. " \
                    f"Make sure you have developer mode enabled and right click the message you want users to react to and `Copy ID`.\n\u200b\n"
    if ctx.author.id in [600549104015114270, 170992935951794176]:
        owner = f"\n\u200b\n:bangbang: Owner Commands :bangbang:\n" \
                f"`{prefix}adminrole <role>` - Sets the role that can use all moderator commands.\n\u200b\n" \
                f"`{prefix}removeadminrole` - Removes the role that is able to use all moderator commands."
    await ctx.author.send(f":scroll: __Help Menu__ :scroll:\n\u200b{general}")
    if data["admin_role"] in [role.id for role in ctx.author.roles]:
        await ctx.author.send(moderator)
    if ctx.author.id in [600549104015114270, 170992935951794176]:
        await ctx.author.send(owner)
    await ctx.send(":incoming_envelope:")

extensions = ["events", "levels", "moderation"]

if __name__ == '__main__':
    for count, extension in enumerate(extensions, 1):
        try:
            bot.load_extension(extension)
            print(f"Successfully loaded extension {count}/{len(extensions)}: {extension}")
        except Exception as e:
            print(f'Failed to load extension {count}/{len(extensions)}: {extension}', file=sys.stderr)
            traceback.print_exc()


bot.run("NjEwMjg0MjMwNzY0NjU4NzA4.XVDBow.lKZI1hH5vYdTAJhW6dcbYVyrkbU", reconnect=True, bot=True)
