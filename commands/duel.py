import asyncio
import discord
from discord import app_commands
from typing import Union

def setup(bot):
    @bot.tree.command(name="duel", description="duel against another person")
    @app_commands.describe(opponent = "Name the person you would like to duel", bet_amount = "The amount you would like to bet (Optional)")
    async def duel(interaction: discord.Interaction, opponent: discord.Member, bet_amount: Union[int, None] = None):
        if bet_amount is None:
            await interaction.response.send_message(f"{interaction.user.display_name} ran the duel command against <@{opponent.id}> without a bet amount!")
        else:
            await interaction.response.send_message(f"{interaction.user.name} ran the duel command against {opponent}!")

        async def duel_timeout():
            await asyncio.sleep(30)
            await interaction.edit_original_response(content="The duel has timed out.")

        timeout_task = bot.loop.create_task(duel_timeout())

        if bet_amount is not None:
            timeout_task.cancel()