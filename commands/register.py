import discord
import datetime
import pymongo

def setup(bot, db_collection):
    @bot.tree.command(name="register", description="Registers the user to the game.")
    async def register(interaction: discord.Interaction):
        try:
            test_user = {"_id": interaction.user.name,
                         "balance": 100,
                         "cards": [0] * 14,
                         "deck": [[0] * 14 for _ in range(5)],
                         "last_pull_time": datetime.datetime.now(),
                         "packs": 10,
                         "total": 0,
                         "total_pulls": 0}
            db_collection.insert_one(test_user)
            await interaction.response.send_message(f"{test_user['_id']} has been successfully registered.")
        except pymongo.errors.DuplicateKeyError:
            await interaction.response.send_message(f"{interaction.user.name} is already a registered user.")
