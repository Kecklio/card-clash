import discord
from typing import Union

# utils import
from utils import card_mapping

def setup(bot, db_collection):
    @bot.tree.command(name="cheat", description="Cheat all Jokers")
    async def cheat(interaction: discord.Interaction, code: Union[str, None] = None):
        user = db_collection.find_one({"_id":interaction.user.name})
        if user is None:
            await interaction.response.send_message(f"You must register first by using /register")
            return
        if code == "pulls":
            user = user = db_collection.find_one({"_id":interaction.user.name})
            db_collection.update_one(
                {"_id": interaction.user.name},
                {"$set": {"packs": user["packs"] + 10, "last_pull_time": user["last_pull_time"]}}
            )
        elif code == "stop":
            await interaction.response.send_message("Bot has been successfully shut down.")
            exit()
        elif code == "clear_database":
            db_collection.delete_many({})
            await interaction.response.send_message("Database has been successfully cleared.")
        await interaction.response.send_message(card_mapping[14]*5)