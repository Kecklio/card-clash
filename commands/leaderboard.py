import discord
from discord import app_commands
from discord.app_commands import Choice

def setup(bot, db_collection):
    @bot.tree.command(name="leaderboard", description="Display the top players in every category.")
    @app_commands.choices(type=[
        Choice(name='Balance', value='balance'),
        Choice(name='Total Cards', value='total'),
        Choice(name='Total Pulls', value='total_pulls'),
        Choice(name='Jokers Pulled', value='joker'),
    ])
    async def leaderboard(interaction: discord.Interaction, type: app_commands.Choice[str]):
        # Fetch data from MongoDB
        user_data = {}
        key = type.value
        v_name = type.name
        for user in db_collection.find():
            user_data[user['_id']] = {
                'balance': user.get('balance', 0),
                'total': user.get('total', 0),
                'total_pulls': user.get('total_pulls', 0),
                'cards': user.get('cards', []),
                'deck': user.get('deck', [[0]*14 for _ in range(5)])
            }
        if key == 'joker':
            sorted_users = sorted(user_data.items(), key=lambda x: x[1]['cards'][13] if len(x[1]['cards']) > 13 else 0, reverse=True)[:5]
        else:
            sorted_users = sorted(user_data.items(), key=lambda x: x[1].get(key, 0), reverse=True)[:5]

        leaderboard_message = f"Top 5 users by {type.name}:\n"
        for idx, (user, data) in enumerate(sorted_users, start=1):
            if key == 'joker':
                jokers = data['cards'][13]
                for i in range(5):
                    jokers += data['deck'][i][13]
                leaderboard_message += f"{idx}. **{user}** - {jokers} Jokers Pulled\n"
            else:
                leaderboard_message += f"{idx}. **{user}** - {'$' if key == 'balance' else ''}{data.get(key, 0)} {v_name if key != 'balance' else ''}\n"

        await interaction.response.send_message(leaderboard_message)