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

bot =commands.Bot(command_prefix='!', intents=intents)

#============================File Handling===============================================================================================
CSV_file = "C:/Users/malic/Documents/Code/PythonProjects/Discord Bots/Summoner/PlayerStats.csv"
#================================================Monsters=======================================================

monster_list = {
    "slime":  {"name": "Slime",  "hp": 30, "attack": 5,  "xp": 10},
    "goblin": {"name": "Goblin", "hp": 50, "attack": 10, "xp": 20},
    "orc":    {"name": "Orc",    "hp": 80, "attack": 15, "xp": 40}
                }
#monster = random.choice(list(monster_list.values()))

#============================================Functions====================================================================================

def player_check(userid):
    #something that returns true or false to see if the player is in the ods sheet then return true or false?
    #rest of code starts with playercheck == True then proceed else message about needing to register first
    #maybe also need to add responses to message reactions if ID isnt in here
    df = pd.read_csv(CSV_file)
    user = userid
    return str(user) in df["Discord_ID"].astype(str).values


def register_player(userid, username):  #!register
    user = userid
    name = username
    now = dt.now()
    add_user = pd.DataFrame([{
        "Discord_Username": username,
        "Discord_ID": str(userid),
        "Join_Date": now,
        "Player_LVL": 0,
        "Player_EXP":0,
        "Player_Current_HP": 50,
        "Player_Current_ATK": 15,
        "Last_Healed": now
    }])

    if not os.path.exists(CSV_file):
        add_user.to_csv(CSV_file, index=False)
    else:
        add_user.to_csv(CSV_file, mode="a", index=False, header=False)



def healthcheck(userid):
    df = pd.read_csv(CSV_file)
    user = userid
    hp = df.loc[df["Discord_ID"] == user, "Player_Current_HP"].values

    if len(hp) > -1:
        return hp
    else:
        return

def isAlive(userid):
    df = pd.read_csv(CSV_file)
    user = userid
    hp = df.loc[df["Discord_ID"] == user, "Player_Current_HP"].values

    if hp > 0:
        return True
    else:
        return False

def levelcheck(userid):
    df = pd.read_csv(CSV_file)
    user = userid
    player_level = df.loc[df["Discord_ID"] == user, "Player_LVL"].values

    if len(player_level) > 0:
        return player_level
    else:
        return


def levelup_check(userid): #put into the end of each battle to check in next level acheived
    df = pd.read_csv(CSV_file)
    user = userid
    level = df.loc[df["Discord_ID"] == user, "Player_LVL"].values
    EXP = df.loc[df["Discord_ID"] == user, "Player_EXP"].values
    
    if level == 0 and EXP <=99:
        return True
    elif level == 1 and EXP >=100:
        new_level = 2
        new_ATK = 20
        df.loc[df["Discord_id"] == user, ["Player_LVL", "Player_Current_ATK"]] = [new_level,new_ATK]
        df.to_csv(CSV_file, index=False)
        return True
    elif level == 2 and EXP >=200:
        new_level = 3
        new_ATK = 30
        df.loc[df["Discord_id"] == user, ["Player_LVL", "Player_Current_ATK"]] = [new_level,new_ATK]
        df.to_csv(CSV_file, index=False)
        return True
    else:
        return True

'''
def HP_restore(userid):    #!restore
    #check if the last time they healed was an hour ago and allow if its been an hour. deny if it hasnt been
    df = pd.read_csv(CSV_file)
    user= userid
    last_healed = df.loc[df["Discord_ID"] == user, "Last_Healed"].values
    now = dt.now()
    time_difference = now - last_healed
    heal_cooldown = td(hours=1)
    #time_remaining = heal_cooldown - time_difference

    if now >= last_healed + heal_cooldown:
        if levelcheck(user) == 0:
            new_hp = 50
            df.loc[df["Discord_id"] == user, ["Player_Current_HP", "Last_healed"]] = [new_hp, now]
            df.to_csv(CSV_file, index=False)
            return True
        elif levelcheck(user) == 1:
            new_hp = 100
            df.loc[df["Discord_id"] == user, ["Player_Current_HP", "Last_healed"]] = [new_hp, now]
            df.to_csv(CSV_file, index=False)
            return True
        elif levelcheck(user) == 2:
            new_hp = 150
            df.loc[df["Discord_id"] == user, ["Player_Current_HP", "Last_healed"]] = [new_hp, now]
            df.to_csv(CSV_file, index=False)
            return True
        elif levelcheck(user) == 3:
            new_hp = 200
            df.loc[df["Discord_id"] == user, ["Player_Current_HP", "Last_healed"]] = [new_hp, now]
            df.to_csv(CSV_file, index=False)
            return True
        else:
            new_hp = 250
            df.loc[df["Discord_id"] == user, ["Player_Current_HP", "Last_healed"]] = [new_hp, now]
            df.to_csv(CSV_file, index=False)
            return True
    #or dont and return False and time remaining (dunno if it works like that)
    else:
        return False
'''

'''
def HP_restore(userid):
    # Read once, enforce types
    df = pd.read_csv(
        CSV_file,
        dtype={"Discord_ID": str},            # store IDs as strings
        parse_dates=["Last_Healed"],          # parse to datetime if present
    )

    uid = str(userid)

    # Ensure required columns exist
    if "Last_Healed" not in df.columns:
        df["Last_Healed"] = pd.NaT
    if "Player_Current_HP" not in df.columns:
        df["Player_Current_HP"] = 0

    # Find the row for this user
    mask = (df["Discord_ID"].astype(str) == uid)
    if not mask.any():
        # Not registered (your player_check should catch this, but be safe)
        return (False, None)

    last_healed = df.loc[mask, "Last_Healed"].iloc[0]

    now = dt.now()
    cooldown = td(hours=1)

    # If never healed before (NaT), allow immediately
    if pd.isna(last_healed):
        ready_at = now - td(seconds=1)
    else:
        ready_at = last_healed + cooldown

    if now >= ready_at:
        lvl = levelcheck(userid)  # expected to return an int

        # 0→50, 1→100, 2→150, 3→200, 4+→250
        new_hp = min(50 + max(int(lvl), 0) * 50, 250)

        df.loc[mask, ["Player_Current_HP", "Last_Healed"]] = [new_hp, now]
        df.to_csv(CSV_file, index=False)
        return (True, None)
    else:
        return (False, ready_at - now)
'''


'''
def fight_monster(userid, monster_name):
    df = pd.read_csv(CSV_file)
    user = userid
    chosen_monster = monster_name
    p_ATK = df.loc[df["Discord_ID"] == user, ""].values
    p_HP = df.loc[df["Discord_ID"] == user, ""].values
    m_ATK = (monster_list[chosen_monster]["attack"])
    m_HP = (monster_list[chosen_monster]["hp"])
'''


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
                await reaction.message.channel.send(
                    f"{user.mention} insert fight functions here: The monster is: {monster_list[monster_name]}"
                    )
                #=========================================================================


                                            #Fight here


                #======================================================================


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


#========================================================================================================

@bot.command()
async def hello(ctx):
    await ctx.send(f"hello {ctx.author.mention}")

@bot.command()
async def level(ctx):
    userid = ctx.author.id
    LVL = levelcheck(userid)
    await ctx.send(f"{ctx.author.mention} is Level {LVL}")

@bot.command()
async def hp(ctx):
    userid = ctx.author.id
    hp = healthcheck(userid)
    await ctx.send(f"{ctx.author.mention} your current hp is {hp}")

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



'''
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
'''
'''
@bot.command()
async def restore(ctx):
    userid = ctx.author.id

    if not player_check(userid):
        await ctx.send(
            f"{ctx.author.mention} is not yet registered to fight! Please sign up with !register"
        )
        return

    success, remaining = HP_restore(userid)

    if success:
        await ctx.send(
            f"{ctx.author.mention} is now fully healthy and ready to do battle again!"
        )
    elif remaining is not None:
        total = int(remaining.total_seconds())
        mins, secs = divmod(total, 60)
        await ctx.send(
            f"{ctx.author.mention}, you must wait {mins}m {secs}s before healing again!"
        )
    else:
        # User not found or unexpected issue; keeps message friendly
        await ctx.send(
            f"{ctx.author.mention}, something went wrong restoring your HP."
        )
'''

@bot.command()
async def summon(ctx):
    monster = random.choice(list(monster_list.values()))
    await ctx.send(f"A wild **{monster['name']}** appears! HP: {monster['hp']} | ATK: {monster['attack']}")


#===============================Run===============================================================================
bot.run(token, log_handler=handler, log_level=logging.DEBUG)