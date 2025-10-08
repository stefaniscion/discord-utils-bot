import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
bump_channel_id = int(os.getenv("BUMP_CHANNEL_ID"))
king_role_id = int(os.getenv("KING_ROLE_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message):
    guild = await bot.fetch_guild(message.guild.id)

    # check if the message is a bump message
    if message.author.display_name == "DISBOARD":
        user_bumper = message.interaction_metadata.user

        # get the crown
        king_role = guild.get_role(king_role_id)

        # remove usurped king
        async for member in guild.fetch_members(limit=None):
            if king_role in member.roles:
                print(f"Removing king role from {member.display_name}")
                await member.remove_roles(king_role)

        # hail to the new king!

        member_bumper = await guild.fetch_member(user_bumper.id)
        print(f"Adding king role to {member_bumper.display_name}")
        await member_bumper.add_roles(king_role)
        announcement_channel = await bot.fetch_channel(bump_channel_id)

        await announcement_channel.send(
            f"All hail the Bump King {member_bumper.mention}! 👑"
        )

    await bot.process_commands(message)


@bot.command()
async def bump(ctx):
    """counts the number of bumps in the channel"""
    channel = ctx.guild.get_channel(bump_channel_id)
    response_message = await ctx.send("Sto contando...")
    leaderboard = {}

    history = channel.history(limit=None)

    async for message in history:
        if message.author.display_name == "DISBOARD":
            user_bumper = message.interaction_metadata.user
            leaderboard[user_bumper] = (
                leaderboard[user_bumper] + 1 if user_bumper in leaderboard else 1
            )
            leaderboard = dict(
                sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)
            )

    response_message_content = "Classifica dei bump:\n"
    for i, (user_bumper, count) in enumerate(leaderboard.items(), start=1):
        response_message_content += f"**{i}.** {user_bumper.mention}: {count} bump\n"

    # edit the original message
    await response_message.edit(content=response_message_content)


bot.run(bot_token)
