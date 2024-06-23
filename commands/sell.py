import discord
from discord import app_commands
from discord.app_commands import Choice
from typing import Union

# utils imports
from utils import card_mapping
from utils import sell_value
from utils import update_total

def setup(bot, db_collection):
    # sell command
    @bot.tree.command(name="sell", description="Sells a number of cards you own.")
    @app_commands.describe(card="The card you want to sell", quantity="The number of cards you want to sell. You can type 'half' or 'all'.")
    @app_commands.choices(card=[
        Choice(name='Ace', value=1),
        Choice(name='2', value=2),
        Choice(name='3', value=3),
        Choice(name='4', value=4),
        Choice(name='5', value=5),
        Choice(name='6', value=6),
        Choice(name='7', value=7),
        Choice(name='8', value=8),
        Choice(name='9', value=9),
        Choice(name='10', value=10),
        Choice(name='Jack', value=11),
        Choice(name='Queen', value=12),
        Choice(name='King', value=13),
        Choice(name='Joker', value=14),
    ])
    async def sell(interaction: discord.Interaction, card: int, quantity: Union[str, None] = None):
        user = db_collection.find_one({"_id":interaction.user.name})
        if user is None:
            await interaction.response.send_message(f"You must register first by using /register")
            return
        cards = user["cards"]
        balance = user["balance"]
        if quantity is None: q = 1
        elif quantity.lower() == 'half': q = int(cards[card-1] / 2)
        elif quantity.lower() == 'all': q = cards[card-1]
        elif quantity.isdigit():
            q = int(quantity)
        else:
            await interaction.response.send_message(f'Quantity "{quantity}" is not a valid amount.')
            return
        if (cards[card-1] < q):
            await interaction.response.send_message(f"You don't have {q}x {card_mapping[card]}. You currently have " + str(cards[card-1]) + ".")
        else:
            cards[card-1] -= q
            balance += sell_value[card]*q
            db_collection.update_one({"_id":interaction.user.name}, { "$set": { "cards": cards, "balance": balance }})
            await interaction.response.send_message(f"Sold {q}x {card_mapping[card]} for ${sell_value[card]*q}.\nNew balance: ${balance}.\nYou now have " + str(cards[card-1]) + " left.")
            update_total(user, db_collection)
            # await interaction.response.send_message(f"Confirm sale of {quantity} number of {card} cards")