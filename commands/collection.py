import discord

# utils import
from utils import update_packs
from utils import update_total
from utils import card_mapping

def setup(bot, db_collection):
    @bot.tree.command(name="collection", description="Displays all of the cards that you own.")
    async def collection(interaction: discord.Interaction):
        user = db_collection.find_one({"_id":interaction.user.name})
        if user is None:
            await interaction.response.send_message(f"You must register first by using /register")
            return
        # update the total number of packs the user has
        update_packs(user, db_collection)
        update_total(user, db_collection)
        cards = user["cards"]
        message = f"Packs: {user['packs']}\n"
        for i in range(14):
            message += str(card_mapping[i+1]) + ":" + str(cards[i]) + "\n"
        message += f'Total: {user["total"]}'
        await interaction.response.send_message(message)