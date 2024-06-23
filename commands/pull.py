import asyncio
import discord
from typing import Union

# utils imports
from utils import card_mapping
from utils import update_packs
from utils import random_card
from utils import update_total

def setup(bot, db_collection):
    @bot.tree.command(name="pull", description="Pull your card packs")
    async def pull(interaction: discord.Interaction, quantity: Union[int, None] = None):
        user = db_collection.find_one({"_id":interaction.user.name})
        if user is None:
            await interaction.response.send_message(f"You must register first by using /register")
            return
        
        if quantity is None: quantity = 1
        update_packs(user, db_collection)
        if user["packs"] - quantity < 0:
            await interaction.response.send_message(f"You do not have {quantity} packs to open")
            return
        if quantity > 10 or quantity < 1:
            await interaction.response.send_message("You must select between 1 and 10 packs to pull.")
            return

        async def pull_cards():
            # pulls the 5 cards and adds them to an array
            card_pull = []
            for i in range(5*quantity):
                pull = random_card()
    #            if roll_for_shiny():   To do later sometime whatever
                if pull in {1, 11, 12, 13, 14} or quantity > 1:
                    card_pull.append(pull)
                else:
                    card_pull.insert(0, pull)

            # displays the 5 cards in the chat
            if quantity > 1:
                mapped_cards = [card_mapping[card] for card in card_pull]
                message = f"Successfully opened {quantity} packs:\n"
                for i in range(0, len(mapped_cards), 5):
                    message += ' '.join(mapped_cards[i:i+5]) + '\n'
                await interaction.response.send_message(message)
            else:
                message = [card_mapping[0]] * 5
                await interaction.response.send_message("".join(message))
                for x in range(5):
                    await asyncio.sleep(0.3)
                    if card_pull[x] in {1, 11, 12, 13, 14}:
                        await asyncio.sleep(0.7)
                    message[x] = card_mapping[card_pull[x]]
                    output_message = "".join(message)
                    await interaction.edit_original_response(content=output_message)
                await interaction.followup.send(f"{interaction.user.name} has "+str(user["packs"] - 1)+" packs left."+("\nGZ ON THE JOKER!!! :star_struck:" if 14 in card_pull else ""))

            # adds the cards to the database
            cards = user["cards"]
            for card in card_pull:
                cards[int(card)-1] += 1
            db_collection.update_one({"_id":interaction.user.name}, {"$set":{"cards":cards}})
            update_total(user, db_collection)

        if user["packs"] > 0:
            db_collection.update_one({"_id":interaction.user.name}, {"$set":{"packs":user["packs"]-quantity, "total_pulls": user["total_pulls"]+(quantity*5)}})
            bot.loop.create_task(pull_cards())
        else:
            await interaction.response.send_message(f"You do not have any card packs available to pull :sob:")