import discord

def setup(bot, db_collection):
    @bot.tree.command(name="balance", description="Displays the user's balance.")
    async def balance(interaction: discord.Interaction):
        user = db_collection.find_one({"_id": interaction.user.name})
        if user:
            await interaction.response.send_message(f"{interaction.user.name}, your balance is {user['balance']} coins.")
        else:
            await interaction.response.send_message(f"{interaction.user.name}, you are not registered. Please use /register to register.")
