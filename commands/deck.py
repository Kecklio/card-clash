import discord
from discord import app_commands
from discord.app_commands import Choice
from typing import Union

# utils imports
from utils import card_mapping

def setup(bot, db_collection):
    @bot.tree.command(name="deck", description="Build and modify any deck.")
    @app_commands.describe(number="Deck Number",
                        modification="What you would like to do to the deck",
                        card="which card you would like to modify.",
                        quantity="How many cards you would like to modify.")
    @app_commands.choices(number=[Choice(name=1, value=0),
                                Choice(name=2, value=1),
                                Choice(name=3, value=2),
                                Choice(name=4, value=3),
                                Choice(name=5, value=4)])
    @app_commands.choices(modification=[Choice(name='add', value='add'),
                                        Choice(name='remove', value='remove'),
                                        Choice(name='view', value='view')])
    @app_commands.choices(card=[Choice(name='Ace', value=1),
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
                                Choice(name='Joker', value=14),])
    async def deck(interaction: discord.Interaction, number: app_commands.Choice[int], modification: app_commands.Choice[str], card: Union[app_commands.Choice[int], None] = None, quantity: Union[int, None] = None):
        user = db_collection.find_one({"_id":interaction.user.name})
        if user is None:
            await interaction.response.send_message(f"You must register first by using /register")
            return
        if quantity is None: quantity = 1
        
        # view modification
        if modification.value == 'view':
            message = f"Deck {number.name}:\n"
            cards = user["deck"][number.value]
            for i in range(14):
                if cards[i] > 0:
                    message += str(card_mapping[i+1]) + ":" + str(cards[i]) + "\n"
            message += f'Total: {sum(cards)}/50'
            await interaction.response.send_message(message)
        
        # add modification
        elif modification.value == 'add':
            if card is None:
                await interaction.response.send_message("Please enter a card to add")
                return
            card_amount = user["cards"][card.value-1]
            if card_amount < quantity:
                await interaction.response.send_message(f"You do not have enough {card} cards to add to deck {number.name}.")
                return
            
            # Calculate the current total number of cards in the deck
            current_deck_total = sum(user["deck"][number.value])
            if current_deck_total + quantity > 50:
                await interaction.response.send_message(f"Cannot add {quantity}x {card_mapping[card.value]} to deck {number.name}. The total number of cards in the deck cannot exceed 50.")
                return

            # Update the deck and cards array
            new_deck_value = user["deck"][number.value][card.value-1] + quantity
            new_card_value = user["cards"][card.value-1] - quantity

            # Update the user document
            db_collection.update_one(
                {"_id": interaction.user.name},
                {
                    "$set": {
                        f"deck.{number.value}.{card.value-1}": new_deck_value,
                        f"cards.{card.value-1}": new_card_value
                    }
                }
            )
            await interaction.response.send_message(f"Successfully added {quantity}x {card_mapping[card.value]} to deck {number.name}.")
        
        # remove modification
        elif modification.value == 'remove':
            if card is None:
                await interaction.response.send_message("Please enter a card to remove")
                return
            deck_card_amount = user["deck"][number.value][card.value-1]
            if deck_card_amount < quantity:
                await interaction.response.send_message(f"You do not have {quantity}x {card_mapping[card.value]} in deck {number.name} to remove.")
                return
            # Update the deck and cards array
            new_deck_value = user["deck"][number.value][card.value-1] - quantity
            new_card_value = user["cards"][card.value-1] + quantity

            # Update the user document
            db_collection.update_one(
                {"_id": interaction.user.name},
                {
                    "$set": {
                        f"deck.{number.value}.{card.value-1}": new_deck_value,
                        f"cards.{card.value-1}": new_card_value
                    }
                }
            )
            await interaction.response.send_message(f"Successfully removed {quantity}x {card_mapping[card.value]} from deck {number.name}.")