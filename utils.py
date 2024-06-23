import datetime
import random

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

def update_packs(user, db_collection):
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

def update_total(user, db_collection):
    total = 0
    for num in user["cards"]:
        total += num
    db_collection.update_one({"_id": user["_id"]}, {"$set": {"total": total}})

def roll_for_shiny():
    rand_num = random.randint(1, 1000)
    return rand_num == 1000

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
