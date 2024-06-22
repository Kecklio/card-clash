import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from typing import Union
import asyncio
import random
import pymongo
from pymongo import MongoClient
import datetime

# connect to Mongo DB
mongo_link = open('mongo link.txt', 'r').read()
cluster = MongoClient(mongo_link)
db = cluster["cardClash"]
db_collection = db["users"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="-", intents=intents)

card_mapping = {
    0: "<:Back:1253556770274803762>",
    1: "<:Ace:1253556703950016534>",
    2: "<:2_:1253556692839567370>",
    3: "<:3_:1253556693955117066>",
    4: "<:4_:1253556694575878146>",
    5: "<:5_:1253556696211656714>",
    6: "<:6_:1253556697226543226>",
    7: "<:7_:1253556698082443275>",
    8: "<:8_:1253556699059585034>",
    9: "<:9_:1253556699910901760>",
    10: "<:10:1253556769154797589>",
    11: "<:Jack:1253556771554070569>",
    12: "<:Queen:1253556714070872184>",
    13: "<:King:1253556772589928538>",
    14: "<:Joker:1253556710510039110>"
}

sell_value = {
    1: 20,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
    11: 25,
    12: 30,
    13: 35,
    14: 50
}


@bot.event
async def on_ready() -> None:
    try:
        synced = await bot.tree.sync()
        print(f'{bot.user} is now running with {len(synced)} command(s)!')
    except Exception as e:
        print(e)


# register command
@bot.tree.command(name="register", description="Registers the user to the game.")
async def register(interaction: discord.Interaction):
    try:
        test_user = {"_id":interaction.user.name,
                    "balance": 100,
                    "cards":[0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    "deck":[
                        [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                    ],
                    "last_pull_time":datetime.datetime.now(),
                    "packs": 10,
                    "total": 0,
                    "total_pulls": 0}
        db_collection.insert_one(test_user)
        await interaction.response.send_message(f"{test_user['_id']} has been successfully registered.")
    except pymongo.errors.DuplicateKeyError:
        await interaction.response.send_message(f"{test_user['_id']} is already a registered user.")


# balance command
@bot.tree.command(name="balance", description="Check your current balance.")
async def balance(interaction: discord.Interaction):
    user = db_collection.find_one({"_id":interaction.user.name})
    if user is None:
        await interaction.response.send_message(f"You must register first by using /register")
        return
    balance = user["balance"]
    await interaction.response.send_message(f"You currently have a balance of ${balance}.")


# buy command
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


# cheat command
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
        update_total(user)
    elif code == "stop":
        await interaction.response.send_message("Bot has been successfully shut down.")
        exit()
    elif code == "clear_database":
        db_collection.delete_many({})
        await interaction.response.send_message("Database has been successfully cleared.")
    await interaction.response.send_message("<:Joker:1245924447727390832>"*5)


# collection command
@bot.tree.command(name="collection", description="Displays all of the cards that you own.")
async def collection(interaction: discord.Interaction):
    user = db_collection.find_one({"_id":interaction.user.name})
    if user is None:
        await interaction.response.send_message(f"You must register first by using /register")
        return
    # update the total number of packs the user has
    update_packs(user)
    update_total(user)
    cards = user["cards"]
    message = f"Packs: {user['packs']}\n"
    for i in range(14):
        message += str(card_mapping[i+1]) + ":" + str(cards[i]) + "\n"
    message += f'Total: {user["total"]}'
    await interaction.response.send_message(message)


# deck command
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

# leaderboard command
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


# pull command
@bot.tree.command(name="pull", description="Pull your card packs")
async def pull(interaction: discord.Interaction, quantity: Union[int, None] = None):
    user = db_collection.find_one({"_id":interaction.user.name})
    if user is None:
        await interaction.response.send_message(f"You must register first by using /register")
        return
    
    if quantity is None: quantity = 1
    update_packs(user)
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
        update_total(user)

    if user["packs"] > 0:
        db_collection.update_one({"_id":interaction.user.name}, {"$set":{"packs":user["packs"]-quantity, "total_pulls": user["total_pulls"]+(quantity*5)}})
        bot.loop.create_task(pull_cards())
    else:
        await interaction.response.send_message(f"You do not have any card packs available to pull :sob:")


# prices command
@bot.tree.command(name="prices", description="Displays all prices of cards.")
async def prices(interaction: discord.Interaction):
    message = (f"{card_mapping[2]}: $2\n"
                f"{card_mapping[3]}: $3\n"
                f"{card_mapping[4]}: $4\n"
                f"{card_mapping[5]}: $5\n"
                f"{card_mapping[6]}: $6\n"
                f"{card_mapping[7]}: $7\n"
                f"{card_mapping[8]}: $8\n"
                f"{card_mapping[9]}: $9\n"
                f"{card_mapping[10]}]: $10\n"
                f"{card_mapping[1]}: $20\n"
                f"{card_mapping[11]}: $25\n"
                f"{card_mapping[12]}: $30\n"
                f"{card_mapping[13]}: $35\n"
                f"{card_mapping[14]}: $50")
    await interaction.response.send_message(message)


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
        update_total(user)
        # await interaction.response.send_message(f"Confirm sale of {quantity} number of {card} cards")



# FUNCTION LIST

# update the number of packs a person has
def update_packs(user):
    now = datetime.datetime.now()
    last_pull_time = user["last_pull_time"]
    if isinstance(last_pull_time, float):
        last_pull_time = datetime.datetime.fromtimestamp(last_pull_time)
    time_since_last_pull = (now - last_pull_time).total_seconds() / 60
    if time_since_last_pull > 15:
        accumulated_packs = min(5, int(time_since_last_pull // 15))
        user["packs"] += accumulated_packs
        
        user["last_pull_time"] = now.timestamp()
        db_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"packs": user["packs"], "last_pull_time": user["last_pull_time"]}}
        )

# update total number of cards owned
def update_total(user):
    total = 0
    for num in user["cards"]:
        total += num
    db_collection.update_one({"_id": user["_id"]}, {"$set": {"total": total}})


# roll for a shiny card
def roll_for_shiny():
    rand_num = random.randint(1, 1000)
    return rand_num == 1000

# select a random card
def random_card():
    rand_num = random.randint(1, 200)
    
    if rand_num <= 28:  # 14% probability
        return 2
    elif rand_num <= 54:  # 13% probability
        return 3
    elif rand_num <= 78:  # 12% probability
        return 4
    elif rand_num <= 100:  # 11% probability
        return 5
    elif rand_num <= 120:  # 10% probability
        return 6
    elif rand_num <= 138:  # 9% probability
        return 7
    elif rand_num <= 154:  # 8% probability
        return 8
    elif rand_num <= 168:  # 7% probability
        return 9
    elif rand_num <= 180:  # 6% probability
        return 10
    elif rand_num <= 190:  # 5% probability
        return 1 # Ace
    elif rand_num <= 194:  # 2% probability
        return 11 # Jack
    elif rand_num <= 197:  # 1.5% probability
        return 12 # Queen
    elif rand_num <= 199:  # 1% probability
        return 13 # King
    else:  # 0.5% probability
        return 14 # Joker


@bot.tree.command(name="duel", description="duel against another person")
@app_commands.describe(opponent = "Name the person you would like to duel", bet_amount = "The amount you would like to bet (Optional)")
async def duel(interaction: discord.Interaction, opponent: discord.Member, bet_amount: Union[int, None] = None):
    if bet_amount is None:
        await interaction.response.send_message(f"{interaction.user.display_name} ran the duel command against <@{opponent.id}> without a bet amount!")
    else:
        await interaction.response.send_message(f"{interaction.user.name} ran the duel command against {opponent}!")

    async def duel_timeout():
        await asyncio.sleep(30)
        await interaction.edit_original_response(content="The duel has timed out.")

    timeout_task = bot.loop.create_task(duel_timeout())

    if bet_amount is not None:
        timeout_task.cancel()

    
token = open('token.txt', 'r')
bot.run(token.read())