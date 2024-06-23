import discord

# utils imports
from utils import card_mapping
from utils import sell_value

def setup(bot):
    @bot.tree.command(name="prices", description="Displays all prices of cards.")
    async def prices(interaction: discord.Interaction):
        for i in range(14):
            message += f"{card_mapping[i+1]}: ${sell_value[i+1]}\n"
        await interaction.response.send_message(message)