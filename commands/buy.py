import discord
from discord import app_commands
from typing import Union

def setup(bot, db_collection):
    @bot.tree.command(name="buy", description="Buy a number of card packs")
    @app_commands.describe(quantity="The number of card packs you want to buy")
    async def buy(interaction: discord.Interaction, quantity: Union[str, None] = None):
        user = db_collection.find_one({"_id":interaction.user.name})
        balance = user['balance']
        if user is None:
            await interaction.response.send_message(f"You must register first by using /register")
            return
        pack_cost = 75
        if quantity is None: quantity = 1
        elif quantity.lower() == 'half': quantity = int(max(1, (balance / 75) // 2))
        elif quantity.lower() == 'all': quantity = int(max(1, balance // 75))
        elif quantity.isdigit() == False:
            await interaction.response.send_message(f"Please enter a number or half/all.")
            return
        quantity = int(quantity)
        if user["balance"] > (quantity * pack_cost):
            user["balance"] -= (quantity * pack_cost)
            user["packs"] += quantity
            db_collection.update_one({"_id":interaction.user.name}, { "$set": { "balance": user["balance"], "packs": user["packs"] }})

            await interaction.response.send_message(f"Succesfully purchased {quantity} packs for ${quantity*pack_cost}.")
        else:
            await interaction.response.send_message(f"Cannot buy {quantity}x packs for ${quantity*pack_cost}. Current Balance: {user['balance']}.")