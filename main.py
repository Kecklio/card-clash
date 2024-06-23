import discord
from discord.ext import commands
from pymongo import MongoClient

# connect to Mongo DB
mongo_link = open('mongo link.txt', 'r').read()
cluster = MongoClient(mongo_link)
db = cluster["cardClash"]
db_collection = db["users"]

# bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="-", intents=intents)

# import commands as setup functions
from commands.balance import setup as setup_balance
from commands.buy import setup as setup_buy
from commands.cheat import setup as setup_cheat
from commands.collection import setup as setup_collection
from commands.deck import setup as setup_deck
from commands.duel import setup as setup_duel
from commands.leaderboard import setup as setup_leaderboard
from commands.pull import setup as setup_pull
from commands.prices import setup as setup_prices
from commands.register import setup as setup_register
from commands.sell import setup as setup_sell

# setup commands
setup_balance(bot, db_collection)
setup_buy(bot, db_collection)
setup_cheat(bot, db_collection)
setup_collection(bot, db_collection)
setup_deck(bot, db_collection)
setup_duel(bot)
setup_leaderboard(bot, db_collection)
setup_pull(bot, db_collection)
setup_prices(bot)
setup_register(bot, db_collection)
setup_sell(bot, db_collection)

@bot.event
async def on_ready() -> None:
    try:
        synced = await bot.tree.sync()
        print(f'{bot.user} is now running with {len(synced)} command(s)!')
    except Exception as e:
        print(e)
    
# run the bot
token = open('token.txt', 'r')
bot.run(token.read())