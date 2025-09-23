import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import pandas as pd
import os
import random
from datetime import datetime as dt, timedelta as td
import asyncio


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log',encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True

bot =commands.Bot(command_prefix='~', intents=intents)

#============================File Handling===============================================================================================
CSV_file = "C:/Users/malic/Documents/Code/PythonProjects/Discord Bots/Summoner/PlayerStats.csv"
#================================================Monsters=======================================================

monster_list = {
    "slime":  {"name": "Slime",  "hp": 30, "attack": 5,  "xp": 10},
    "goblin": {"name": "Goblin", "hp": 50, "attack": 8, "xp": 20},
    "orc":    {"name": "Orc",    "hp": 60, "attack": 12, "xp": 40}
                }
#monster = random.choice(list(monster_list.values()))

#============================================Functions====================================================================================

def player_check(userid):
    df = pd.read_csv(CSV_file)
    user = userid
    return str(user) in df["Discord_ID"].astype(str).values


def register_player(userid, username):  #!register
    user = userid
    name = username
    now = dt.now().isoformat(timespec="seconds")
    add_user = pd.DataFrame([{
        "Discord_Username": username,
        "Discord_ID": str(userid),
        "Join_Date": now,
        "Player_LVL": 0,
        "Player_EXP":0,
        "Player_Current_HP": 50,
        "Player_Current_ATK": 15,
        "Last_Healed_Time)": now
    }])

    if not os.path.exists(CSV_file):
        add_user.to_csv(CSV_file, index=False)
    else:
        add_user.to_csv(CSV_file, mode="a", index=False, header=False)


def get_stats(userid): #!stats
    df = pd.read_csv(CSV_file)
    user = userid
    level = df.loc[df["Discord_ID"] == user, "Player_LVL"].values[0]
    exp = df.loc[df["Discord_ID"] == user, "Player_EXP"].values[0]
    hp = df.loc[df["Discord_ID"] == user, "Player_Current_HP"].values[0]
    atk = df.loc[df["Discord_ID"] == user, "Player_Current_ATK"].values[0]
    player = df.loc[df["Discord_ID"]== user, "Discord_Username"].values[0]

    stats_message_parts = []

    while True:
        stats_message_parts.append(f"{player} is at level {level}")
        stats_message_parts.append(f"HP = {hp}")
        stats_message_parts.append(f"ATK = {atk}")
        stats_message_parts.append(f"EXP = {exp}")

        return "\n".join(stats_message_parts)
    

def isAlive(userid):
    df = pd.read_csv(CSV_file)
    user = userid
    hp = df.loc[df["Discord_ID"] == user, "Player_Current_HP"].values[0]

    if hp > 0:
        return True
    else:
        return False


def levelup_check(userid): #see if this should level up
    df = pd.read_csv(CSV_file)
    user = userid
    level = df.loc[df["Discord_ID"] == user, "Player_LVL"].values[0]
    EXP = df.loc[df["Discord_ID"] == user, "Player_EXP"].values[0]

    if level == 0 and EXP <=99:
        return False
    elif level == 1 and EXP >=100:
        return True
    elif level == 2 and EXP >=200:
        return True
    else:
        return False

        

def levelup(userid):
    df = pd.read_csv(CSV_file)
    user = userid
    level = df.loc[df["Discord_ID"] == user, "Player_LVL"].values[0]
    EXP = df.loc[df["Discord_ID"] == user, "Player_EXP"].values[0]
    
    if level == 1 and EXP >=100:
        new_level = 2
        new_ATK = 20
        df.loc[df["Discord_ID"] == user, ["Player_LVL", "Player_Current_ATK"]] = [new_level,new_ATK]
        df.to_csv(CSV_file, index=False)
        return new_level
    elif level == 2 and EXP >=200:
        new_level = 3
        new_ATK = 30
        df.loc[df["Discord_ID"] == user, ["Player_LVL", "Player_Current_ATK"]] = [new_level,new_ATK]
        df.to_csv(CSV_file, index=False)
        return new_level
    else:
        new_level = level
        return new_level


def HP_restore(userid):    #!restore
    df = pd.read_csv(CSV_file)
    user= userid
    level = df.loc[df["Discord_ID"] == user, "Player_LVL"].values[0]
    last_healed_str = df.loc[df["Discord_ID"] == user, "Last_Healed"].values[0]
    last_healed = dt.fromisoformat(last_healed_str)

    now = dt.now()
    heal_cooldown = td(hours=1)

    if now >= last_healed + heal_cooldown:
        if level == 0:
            new_hp = 50
            df.loc[df["Discord_ID"] == user, ["Player_Current_HP", "Last_Healed"]] = [new_hp, now.isoformat(timespec="seconds")]
            df.to_csv(CSV_file, index=False)
            return True
        elif level == 1:
            new_hp = 100
            df.loc[df["Discord_ID"] == user, ["Player_Current_HP", "Last_Healed"]] = [new_hp, now.isoformat(timespec="seconds")]
            df.to_csv(CSV_file, index=False)
            return True
        elif level == 2:
            new_hp = 150
            df.loc[df["Discord_ID"] == user, ["Player_Current_HP", "Last_Healed"]] = [new_hp, now.isoformat(timespec="seconds")]
            df.to_csv(CSV_file, index=False)
            return True
        elif level == 3:
            new_hp = 200
            df.loc[df["Discord_ID"] == user, ["Player_Current_HP", "Last_Healed"]] = [new_hp, now.isoformat(timespec="seconds")]
            df.to_csv(CSV_file, index=False)
            return True
        else:
            new_hp = 250
            df.loc[df["Discord_ID"] == user, ["Player_Current_HP", "Last_Healed"]] = [new_hp, now.isoformat(timespec="seconds")]
            df.to_csv(CSV_file, index=False)
            return True
    else:
        return False



def fight_monster(userid, monster_name):
    
    df = pd.read_csv(CSV_file)
    user = userid
    chosen_monster = monster_name
    p_ATK = df.loc[df["Discord_ID"] == user, "Player_Current_ATK"].values[0]
    p_HP = df.loc[df["Discord_ID"] == user, "Player_Current_HP"].values[0]
    p_EXP = df.loc[df["Discord_ID"] == user, "Player_EXP"].values[0]
    m_ATK = (monster_list[chosen_monster]["attack"])
    m_HP = (monster_list[chosen_monster]["hp"])
    m_XP = (monster_list[chosen_monster]["xp"])
    player = df.loc[df["Discord_ID"]== user, "Discord_Username"].values[0]

    turn = 0
    message_parts = []
    final_message = "\n".join(message_parts)

    while p_HP > 0 and m_HP > 0:
        turn += 1

        m_HP -= p_ATK
        message_parts.append(f"Turn {turn}: {player} hits {chosen_monster} for {p_ATK} damage.")
        if m_HP <= 0:
            message_parts.append(f"The {chosen_monster} has died! You gain {m_XP} EXP!")
            new_player_EXP = p_EXP + m_XP
            df.loc[df["Discord_ID"] == user, ["Player_Current_HP", "Player_EXP"]] = [p_HP, new_player_EXP]
            df.to_csv(CSV_file, index=False)
            if levelup_check(user) == True:
                new_level = levelup(user)
                message_parts.append(f"You are now level {new_level}!")
                return "\n".join(message_parts)
            else:
                return "\n".join(message_parts)

        p_HP -= m_ATK
        message_parts.append(f"{player} takes {m_ATK} from {chosen_monster}")
        if p_HP <= 0: 
            p_HP = 0
            message_parts.append(f"{player} has been knocked out! Try again after you !restore your HP...")
            df.loc[df["Discord_ID"] == user, "Player_Current_HP"] = p_HP
            df.to_csv(CSV_file, index=False)
            return "\n".join(message_parts)    

#reminder for how messages work:
    #message_parts.append(f"message")
    #final_message = "\n".join(message_parts)
    #return final_message

#====================================================== COMMANDS and EVENTS =============================================================
@bot.event
async def on_ready():
    print(f"{bot.user.name} online and ready to rumble...")


active_messages = set()

TIMEOUT = 10 #seconds

@bot.event
async def on_message(message):
    if "appears!" in message.content.lower():
        await message.add_reaction("⚔️")
        active_messages.add(message.id)
        asyncio.create_task(expire_message(message.id, TIMEOUT))
    await bot.process_commands(message)

async def expire_message(message_id, delay):
    await asyncio.sleep(delay)
    active_messages.discard(message_id)

@bot.event
async def on_reaction_add(reaction, user):
    userid = user.id
    if user.bot:
        return
    if str(reaction.emoji) != "⚔️":
        return
    if reaction.message.id not in active_messages:
        return
    if player_check(userid) == True:
        
        if isAlive(userid) == True:
            active_messages.discard(reaction.message.id)#===== Mark as used immediately so no one else can trigger
            msg_content = reaction.message.content.lower()
            found_monster = [m for m in monster_list if m in msg_content]
            if found_monster:
                monster_name = found_monster[0]
                fight_message = fight_monster(userid, monster_name)
                await reaction.message.channel.send(f"{fight_message}")

            else:
                await reaction.message.channel.send(
                    f"{user.mention} something went terribly wrong here, contact a mod...."
                    )
        else:
            await reaction.message.channel.send(
            f"{user.mention} is unconscious, please restore your health with !restore before attempting to fight again"
            )
    else: 
        await reaction.message.channel.send(
        f"{user.mention} is not yet registered to fight! Please sign up with !register"
        )


@bot.command()
async def hello(ctx):
    #leave as test function to see if its alive
    await ctx.send(f"hello {ctx.author.mention}")


@bot.command()
async def stats(ctx):
    userid = ctx.author.id
    stats_message = get_stats(userid)
    await ctx.send(f"{stats_message}")


@bot.command()
async def register(ctx):
    userid = ctx.author.id
    username = ctx.author.name
    try:
        if player_check(userid):
            await ctx.send(f"{ctx.author.mention}, you are already registered.")
        else:
            register_player(userid, username)
            await ctx.send(f"{ctx.author.mention} is now registered!")
    except Exception as e:
        print("Error in player_check:", e)
        await ctx.send("There was an error checking your registration.")


@bot.command()
async def restore(ctx):
    userid = ctx.author.id
    if player_check(userid) == True:
        if HP_restore(userid) == True:
            await ctx.send(f"{ctx.author.mention} is now fully healthy and ready to do battle again!")
        else:
            await ctx.send(f"{ctx.author.mention} please await for more time before healing again!")
    else: 
        await ctx.send(
        f"{ctx.author.mention} is not yet registered to fight! Please sign up with !register"
        )


@bot.command()
async def summon(ctx):
    monster = random.choice(list(monster_list.values()))
    await ctx.send(f"A wild **{monster['name']}** appears! HP: {monster['hp']} | ATK: {monster['attack']}")


@bot.command()
async def howto(ctx):
    lines = [
            "~register : Start out on your adventure here by registering your user ID",
            "~summon : Make a monster appear and press the reaction within 10 seconds to attack it",
            "~restore : Return your HP back to full, once every hour",
            "~stats : Show your current level and statistics",
            "~hello: Makes sure the bot is still alive and responding"
            ]
    await ctx.send(f"\n".join(lines))

#===============================Run===============================================================================
bot.run(token, log_handler=handler, log_level=logging.DEBUG)