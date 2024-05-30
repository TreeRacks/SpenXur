import discord
import asyncio
import datetime
import aiosqlite
import random
import os
import pytz
import requests, zipfile, pickle
import json
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 
from scraper import WebScraper
from handleManifest import get_manifest, build_dict, hashes
from quotes import quotes
from discord.ext import commands
from discord.ext.commands.errors import ChannelNotFound
from dotenv import load_dotenv
from bungio import Client
from bungio.models import (
    BungieMembershipType,
    BungieRewardDisplay,
    DestinyComponentType,
    DestinyHistoricalStatsAccountResult,
    DestinyItemResponse,
    DestinyLeaderboard,
    DestinyLinkedProfilesResponse,
    DestinyProfileResponse,
    DestinyStatsGroupType,
    GetGroupsForMemberResponse,
    GroupApplicationRequest,
    GroupApplicationResponse,
    GroupBanRequest,
    GroupMemberLeaveResult,
    GroupMembershipSearchResponse,
    GroupPotentialMembershipSearchResponse,
    GroupPotentialMemberStatus,
    GroupsForMemberFilter,
    GroupType,
    RuntimeGroupMemberType,
    UserMembershipData,
    BungieMembershipType, 
    DestinyActivityModeType, 
    DestinyUser, 
    UserInfoCard, 
    GeneralUser, 
    CrossSaveUserMembership, 
    DestinyComponentType, 
    DestinyProfileResponse,
    DictionaryComponentResponseOfint32AndDestinyVendorSaleItemComponent,
    DictionaryComponentResponseOfint64AndDestinyCharacterActivitiesComponent,
    DictionaryComponentResponseOfint64AndDestinyCharacterComponent,
    DictionaryComponentResponseOfint64AndDestinyCharacterProgressionComponent,
    DictionaryComponentResponseOfint64AndDestinyCharacterRecordsComponent,
    DictionaryComponentResponseOfint64AndDestinyCharacterRenderComponent,
    DictionaryComponentResponseOfint64AndDestinyCollectiblesComponent,
    DictionaryComponentResponseOfint64AndDestinyCraftablesComponent,
    DictionaryComponentResponseOfint64AndDestinyCurrenciesComponent,
    DictionaryComponentResponseOfint64AndDestinyInventoryComponent,
    DictionaryComponentResponseOfint64AndDestinyKiosksComponent,
    DictionaryComponentResponseOfint64AndDestinyLoadoutsComponent,
    DictionaryComponentResponseOfint64AndDestinyPlugSetsComponent,
    DictionaryComponentResponseOfint64AndDestinyPresentationNodesComponent,
    DictionaryComponentResponseOfint64AndDestinyStringVariablesComponent,
    DictionaryComponentResponseOfuint32AndDestinyPublicVendorComponent,
    DictionaryComponentResponseOfuint32AndDestinyVendorCategoriesComponent,
    DictionaryComponentResponseOfuint32AndDestinyVendorComponent,
    DictionaryComponentResponseOfuint32AndPersonalDestinyVendorSaleItemSetComponent,
    DictionaryComponentResponseOfuint32AndPublicDestinyVendorSaleItemSetComponent,
    PlatformErrorCodes,
    SingleComponentResponseOfDestinyCharacterActivitiesComponent,
    SingleComponentResponseOfDestinyCharacterComponent,
    SingleComponentResponseOfDestinyCharacterProgressionComponent,
    SingleComponentResponseOfDestinyCharacterRecordsComponent,
    SingleComponentResponseOfDestinyCharacterRenderComponent,
    SingleComponentResponseOfDestinyCollectiblesComponent,
    SingleComponentResponseOfDestinyCurrenciesComponent,
    SingleComponentResponseOfDestinyInventoryComponent,
    SingleComponentResponseOfDestinyItemComponent,
    SingleComponentResponseOfDestinyItemInstanceComponent,
    SingleComponentResponseOfDestinyItemObjectivesComponent,
    SingleComponentResponseOfDestinyItemPerksComponent,
    SingleComponentResponseOfDestinyItemPlugObjectivesComponent,
    SingleComponentResponseOfDestinyItemRenderComponent,
    SingleComponentResponseOfDestinyItemReusablePlugsComponent,
    SingleComponentResponseOfDestinyItemSocketsComponent,
    SingleComponentResponseOfDestinyItemStatsComponent,
    SingleComponentResponseOfDestinyItemTalentGridComponent,
    SingleComponentResponseOfDestinyKiosksComponent,
    SingleComponentResponseOfDestinyLoadoutsComponent,
    SingleComponentResponseOfDestinyMetricsComponent,
    SingleComponentResponseOfDestinyPlatformSilverComponent,
    SingleComponentResponseOfDestinyPlugSetsComponent,
    SingleComponentResponseOfDestinyPresentationNodesComponent,
    SingleComponentResponseOfDestinyProfileCollectiblesComponent,
    SingleComponentResponseOfDestinyProfileComponent,
    SingleComponentResponseOfDestinyProfileProgressionComponent,
    SingleComponentResponseOfDestinyProfileRecordsComponent,
    SingleComponentResponseOfDestinyProfileTransitoryComponent,
    SingleComponentResponseOfDestinySocialCommendationsComponent,
    SingleComponentResponseOfDestinyStringVariablesComponent,
    SingleComponentResponseOfDestinyVendorCategoriesComponent,
    SingleComponentResponseOfDestinyVendorComponent,
    SingleComponentResponseOfDestinyVendorGroupComponent,
    SingleComponentResponseOfDestinyVendorReceiptsComponent,
    UserInfoCard,
    DestinyCharacter,
    AuthData
)
from bungio.models.base import BaseModel
from bungio.models.bungie.destiny.responses import DestinyProfileResponse
from requests_oauthlib import OAuth2Session

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='--', intents=intents)
COOLDOWN_RATE_LIMIT = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)
load_dotenv()
async def setup_database():
    async with aiosqlite.connect('messages.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS scheduled_messages
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, message TEXT, channel_id INTEGER, user_id INTEGER)''')
        await db.commit()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has arrived')
    
    await idle_mode()

async def idle_mode():
    while True:
        await setup_database()
        async with aiosqlite.connect('messages.db') as db:
            async with db.execute("SELECT * FROM scheduled_messages WHERE time <= ?", (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)) as cursor:
                messages = await cursor.fetchall()

            for message in messages:
                message_id, time_str, message_text, channel_id, user_id  = message
                # Get the channel object corresponding to the channel_id
                channel = bot.get_channel(channel_id)
                
                if channel:
                    await channel.send(message_text)
                    await delete_message(message_id)

        await asyncio.sleep(5)

@bot.command()
async def shutdown(ctx):
    if ctx.author.id == os.getenv('ADMIN_ID'):
        await ctx.send("Shutting down...")
        await bot.close()
    else:
        await ctx.send("The Nine have not granted you permission to shut me down.")

async def insert_scheduled_message(time_str, message, channel_id, user_id):
    async with aiosqlite.connect('messages.db') as db:
        await db.execute("INSERT INTO scheduled_messages (time, message, channel_id, user_id) VALUES (?, ?, ?, ?)", (time_str, message, channel_id, user_id))
        await db.commit()

def get_channel_if_exists(ctx, channel_name): # helper function to get the channel object if it exists, not used currently
    if channel_name is None:
        channel_name = ctx.channel
        channel = ctx.channel
        print("No channel specified, defaulting to current channel...")
    elif "<" in channel_name and ">" in channel_name and "#" in channel_name:
        # print("Channel specified with ID, attempting to get channel by ID...")
        channel_name = channel_name[channel_name.find("<")+2:channel_name.find(">")]
        channel_id = int(channel_name)
        # print("channel_name is", channel_name)
        # print("channel_id is", channel_id)
        channel = ctx.guild.get_channel(channel_id)
        if channel is None:
            print("Channel not found, defaulting to current channel...")
            channel = ctx.channel
    else:
        return ctx.channel
    return channel

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def echo(ctx, time_str: str, channel: discord.TextChannel = None, *, message):
    try:
        # Parse the time string into a datetime object
        time_format = "%Y-%m-%d %H:%M"
        time_input = datetime.datetime.strptime(time_str, time_format)

        if channel is None:
            await ctx.send("No channel specified, defaulting to current channel...")
            channel = ctx.channel

        if ctx.guild.get_channel(channel.id) is None:
            await ctx.send("This channel does not exist in this server. Only channels in this server can be mentioned.")
            return

        if time_input < datetime.datetime.now():
            await ctx.send("You cannot schedule a message for a time that has already passed...")
            return
        if channel.permissions_for(ctx.guild.me).send_messages:
            await insert_scheduled_message(time_input.strftime("%Y-%m-%d %H:%M:%S"), message, channel.id, ctx.author.id)
            await ctx.send(f"My will is not my own... {ctx.author.display_name} has ordered me to schedule a message for {time_str} PDT, to be sent in channel <#{channel.id}>.")
        else:
            await insert_scheduled_message(time_input.strftime("%Y-%m-%d %H:%M:%S"), message, ctx.channel.id, ctx.author.id)
            await ctx.send(f"My will is not my own... {ctx.author.display_name} has ordered me to schedule a message for {time_str} PDT, to be sent in channel <#{channel.id}>. However, I do not have permission to send messages in that channel. I will send it in <#{ctx.channel.id}> instead.")
        
        
    except ValueError:
        
        await ctx.send("Invalid time. Please use YYYY-MM-DD HH:MM in PDT.")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def echodelay(ctx, delay: int, channel: discord.TextChannel, *, message):
    try:
    
        if channel is None:
            await ctx.send("No channel specified, defaulting to current channel...")
            channel = ctx.channel

        

        # Check if the channel exists in the server
        # Should not be necessary since the channel parameter is a discord.TextChannel object
        if ctx.guild.get_channel(channel.id) is None:
            await ctx.send("This channel does not exist in this server. Only channels in this server can be mentioned.")
            return
        time_input = datetime.datetime.now() + datetime.timedelta(minutes=delay)

        # Insert the message into the database along with the channel ID and user ID
        if channel.permissions_for(ctx.guild.me).send_messages:
            
            await insert_scheduled_message(time_input.strftime("%Y-%m-%d %H:%M:%S"), message, channel.id, ctx.author.id)
            await ctx.send(f"My will is not my own... {ctx.author.display_name} has ordered me to schedule a message to be sent after {delay} minutes in <#{channel.id}>.")
        else:
            await insert_scheduled_message(time_input.strftime("%Y-%m-%d %H:%M:%S"), message, ctx.channel.id, ctx.author.id)
            await ctx.send(f"My will is not my own... {ctx.author.display_name} has ordered me to schedule a message to be sent after {delay} minutes in <#{ctx.channel.id}>. However, I do not have permission to send messages in that channel. I will send it in <#{ctx.channel.id}> instead.")
        
    
    except ValueError:
        
        await ctx.send("Invalid time. Indicate the delay in minutes.")



@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def repeat_echo(ctx, duration: int, interval: int, channel: discord.TextChannel, *, message):
    try:
        # Ensure duration and interval are positive
        if duration <= 0 or interval <= 0:
            await ctx.send("Duration and interval must be positive integers.")
            return

        if channel is None:
            await ctx.send("No channel specified, defaulting to current channel...")
            channel = ctx.channel

        # Check if the channel exists in the server
        if ctx.guild.get_channel(channel.id) is None:
            await ctx.send("This channel does not exist in this server. Only channels in this server can be mentioned.")
            return

        current_time = datetime.datetime.now()
        end_time = current_time + datetime.timedelta(minutes=duration)
        if channel.permissions_for(ctx.guild.me).send_messages:
            # Schedule repetitions until the end time
            while current_time < end_time:
                await insert_scheduled_message(current_time.strftime("%Y-%m-%d %H:%M:%S"), message, channel.id, ctx.author.id)
                current_time += datetime.timedelta(minutes=interval)

            await ctx.send(f"My will is not my own... {ctx.author.display_name} has ordered me to repeat a message every {interval} minutes for {duration} minutes in <#{channel.id}>.")
        else:
            while current_time < end_time:
                await insert_scheduled_message(current_time.strftime("%Y-%m-%d %H:%M:%S"), message, ctx.channel.id, ctx.author.id)
                current_time += datetime.timedelta(minutes=interval)

            await ctx.send(f"My will is not my own... {ctx.author.display_name} has ordered me to repeat a message every {interval} minutes for {duration} minutes in <#{channel.id}>. However, I do not have permission to send messages in that channel. I will send it in <#{ctx.channel.id}> instead.")

    except ValueError:
        await ctx.send("Invalid duration or interval. Please specify positive integers.")

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@echo.error
async def errors(ctx, error):
    if isinstance(error, ChannelNotFound):
        await ctx.send("This channel is either invalid or does not exist in this server... Only channels in this server can be mentioned.")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Your command is either incomplete or incorrect. Please follow the format: `--echo "YYYY-MM-DD HH:MM" <#channel_id> `, followed by your message.')

@echodelay.error
async def errors(ctx, error):
    if isinstance(error, ChannelNotFound):
        await ctx.send("Your specified channel was either invalid or does not exist in this server... Only channels in this server can be mentioned.")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Your command is probably incomplete. Please follow the format: `--echodelay your_delay <#channel_id> `, followed by your message.")

@repeat_echo.error
async def errors(ctx, error):
    if isinstance(error, ChannelNotFound):
        await ctx.send("This channel is either invalid or does not exist in this server... Only channels in this server can be mentioned.")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Your command is either incomplete or incorrect. Please follow the format: `--repeat_echo your_duration your_interval <#channel_id> `, followed by your message.")

@bot.command(name="format")
async def format_echo(ctx):
    embed = discord.Embed(title="__**Format for scheduling messages...**__", color=0x964B00)
    embed.add_field(name="For `--echo`:", value="`--echo \"YYYY-MM-DD HH:MM\" <#channel_id> your_message`", inline=False)
    embed.add_field(name="For `--echodelay`:", value="`--echo your_delay_in_minutes <#channel_id> your_message`", inline=False)
    embed.add_field(name="For `--repeat_echo`:", value="`--repeat_echo duration_in_minutes interval_in_minutes <#channel_id> your_message`", inline=False)
    embed.add_field(name="", value="For example:",inline=False)
    embed.add_field(name="`--echo`:", value="`--echo \"1989-01-01 12:00\" <#valid_channel_id> I am selling terrible loot in the Tower.`", inline=False)
    embed.add_field(name="`--echodelay`:", value="`--echodelay 30 <#valid_channel_id> Send a reminder in 30 minutes.`", inline=False)
    embed.add_field(name="`--repeat_echo`:", value="`--repeat_echo 60 15 <#valid_channel_id> Send a reminder every 15 minutes for an hour.`", inline=False)

    await ctx.send(embed=embed)
    

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def show(ctx):
    async with aiosqlite.connect('messages.db') as db:
        async with db.execute("SELECT * FROM scheduled_messages WHERE user_id = ?", (ctx.author.id,)) as cursor:
            messages = await cursor.fetchall()

            if len(messages) == 0:
                await ctx.send("No scheduled messages.")
                return
            embed = discord.Embed(title=f"__**{ctx.author.display_name} has requested I relay these messages...**__", color=0x964B00)

            message_str = "Scheduled messages:\n"
            for message in messages:
                message_id, time_str, message_text, channel_id, user_id = message
                
                channel = bot.get_channel(channel_id)
                user_name = bot.get_user(user_id).display_name if bot.get_user(user_id) else "Unknown User"
                channel_name = channel.name if channel else "Unknown Channel"
                message_str += f'``Message id: {message_id}`` \n ``{time_str} PDT`` - "{message_text}" \n To channel: <#{channel_id}> from {user_name}\n'
            embed.add_field(name="", value=message_str, inline=False)
            await ctx.send(embed=embed)    

@bot.command()
#admin command: show all messages
@commands.cooldown(1, 10, commands.BucketType.user)
async def showall(ctx):
    if ctx.author.id == os.getenv('ADMIN_ID'):
        async with aiosqlite.connect('messages.db') as db:
            async with db.execute("SELECT * FROM scheduled_messages") as cursor:
                messages = await cursor.fetchall()

            if len(messages) == 0:
                await ctx.send("No scheduled messages.")
                return
            embed = discord.Embed(title="__**Retrieving all scheduled messages...**__", color=0x964B00)

            message_str = "Scheduled messages:\n"
            for message in messages:
                message_id, time_str, message_text, channel_id, user_id = message
                
                channel = bot.get_channel(channel_id)
                user_name = bot.get_user(user_id).display_name if bot.get_user(user_id) else "Unknown User"
                channel_name = channel.name if channel else "Unknown Channel"
                message_str += f'``Message id: {message_id}`` \n ``{time_str} PDT`` - "{message_text}" \n To channel: <#{channel_id}> from {user_name}\n'
                
            embed.add_field(name="", value=message_str, inline=False)
            await ctx.send(embed=embed)
    else:
        await ctx.send("The Nine have not granted you permission to view all scheduled messages.")


async def delete_message(message_id): # helper function for deletion
    async with aiosqlite.connect('messages.db') as db:
        await db.execute("DELETE FROM scheduled_messages WHERE id = ?", (message_id,))
        await db.commit()

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def delete(ctx, message_id: int):
    
    async with aiosqlite.connect('messages.db') as db:
        async with db.execute("SELECT * FROM scheduled_messages WHERE id = ? AND user_id = ?", (message_id, ctx.author.id)) as cursor:

            message = await cursor.fetchone()

        if message is None:
            await ctx.send("Message not found.")
            return

        # check that the user deleting the message is the same user who scheduled it. 
        # this technically shouldn't be reached since the query should return None if the user_id doesn't match ctx.author.id
        if(message[4] != ctx.author.id):
            await ctx.send("You can only delete messages that you scheduled.")
            return
        else:
            await delete_message(message_id)
            await ctx.send("Message deleted.")
    

@bot.command()
#admin command: clear all messages
async def clear(ctx):
    if ctx.author.id == os.getenv('ADMIN_ID'):    
        async with aiosqlite.connect('messages.db') as db:
            await db.execute("DELETE FROM scheduled_messages")
            await db.commit()
        await ctx.send("All messages deleted.")
    else:
        await ctx.send("The Nine have not granted you permission to delete all messages.")


@bot.command()
async def time(ctx):
    await ctx.send(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# @bot.command()
# # function to show the user the format echo command
# async def format(ctx):
#     await ctx.send('To schedule a message, use the following format:```--echo "YYYY-MM-DD HH:MM" (your message without the parentheses)```\nFor example: ```--echo "1989-01-01 00:00" Hello!```')

# (Friday 9 am PST to Tuesday 9 am PST, Friday 4 PM UTC to Monday 4 PM UTC)
def is_within_time_range():
    # Get the current date and time in UTC
    current_time = datetime.datetime.utcnow()

    # Friday
    if current_time.weekday() == 4 and 16 <= current_time.hour <= 23:
        return True

    # Saturday, Sunday, and Monday
    elif current_time.weekday() in [5, 6, 0]: #and 0 <= current_time.hour < 16:
        return True

    elif current_time.weekday() == 1 and current_time.hour < 16:
        return True
    else:
        return False

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def whereisxur(ctx):

    # Create a WebScraper instance
    scraper = WebScraper("https://whereisxur.com/")
    embed = discord.Embed(title="__**A Public Xûrvice Announcement**__", color=0x964B00)
    if is_within_time_range():
        quote = random.choice(quotes)
        # add some text to the embed
        embed.add_field(name = "", value=f'*"{quote}"*', inline=False)
        extracted_data = await scraper.fetch_data()
        current_time = datetime.datetime.utcnow()


        
        # days_str = "day" if days_till_unavailable == 1 else "days"
        # hours_str = "hour" if hours_till_unavailable == 1 else "hours"
        # minutes_str = "minute" if minutes_till_unavailable == 1 else "minutes"


        if extracted_data[''] == "Xûr is at the Tower in the Hangar" or extracted_data[''] == "Xûr is in the Tower Hangar":
            extracted_data[''] = "I am located at the Tower in the Hangar."
            embed.set_thumbnail(url="https://cdna.artstation.com/p/assets/images/images/024/015/060/large/eve-campbell-campbell-hangar-008.jpg?1581036315")
        elif extracted_data[''] == "Xûr is on Nessus at Watcher's Grave":
            extracted_data[''] = "I am located on Nessus at Watcher's Grave."
            embed.set_thumbnail(url="https://destiny.wiki.gallery/images/thumb/4/4e/Watcher%27s_Grave.jpg/1200px-Watcher%27s_Grave.jpg")
        elif extracted_data[''] == "Xûr is at the Tower in the Bazaar":
            embed.set_thumbnail(url="https://www.bungie.net/pubassets/pkgs/132/132448/Bazaar.jpg")

        #embed.add_field(name="", value=f"I will remain there for **{days_till_unavailable} {days_str}, {hours_till_unavailable} {hours_str} and {minutes_till_unavailable} {minutes_str}.**", inline=True)
        if extracted_data:
            for key, value in extracted_data.items():
                # bold the value
                key = f"__**{key}**__" if key else "" 
                embed.add_field(name=key, value=value, inline=False)

        else:
            await ctx.send("Failed to fetch data")
    else:
        current_time = datetime.datetime.utcnow()
        next_friday = current_time + datetime.timedelta((4 - current_time.weekday()) % 7)
        next_friday = next_friday.replace(hour=16, minute=0, second=0, microsecond=0)

    
        time_difference = next_friday - current_time
        days, remainder = divmod(time_difference.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)

        days = int(days)
        hours = int(hours)
        minutes = int(minutes)

        # if current_time.weekday() == 4:
        #     days_till_available = 0
        # else:
        #     days_till_available = 4 - current_time.weekday() - 1 # subtract 1 because monday is 0 and we need to account for monday somehow
            
        # hours_till_available =  (days_till_available + 1)* 24 - current_time.hour
        # print (current_time.hour)
        # minutes_till_available = 60 - current_time.minute

        days_str = "day" if days == 1 else "days"
        hours_str = "hour" if hours == 1 else "hours"
        minutes_str = "minute" if minutes == 1 else "minutes"

        # Format the message with proper grammar
        message = f"I have departed to restock on my wares. I shall return with more terrible things in... \n **{days} {days_str}, {hours} {hours_str} and {minutes} {minutes_str}.**"
        embed.add_field(name="", value=message, inline=False)
        # thumbnail_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xurWantedT.png")
        # # Check if the thumbnail image file exists
        # if os.path.exists(thumbnail_path):
        #     thumbnail_file = discord.File(thumbnail_path, filename="xurWantedT.png")
        #     embed.set_thumbnail(url="attachment://xurWantedT.png")
            
        # else:
        #     await ctx.send("Thumbnail image file not found.")

    await ctx.send(embed=embed)
        
client = Client(
    bungie_client_id=os.getenv('CLIENT_ID'),
    bungie_client_secret=os.getenv('CLIENT_SECRET'),
    bungie_token=os.getenv('API_KEY'),
)
headers = {
    'X-API-Key': os.getenv('API_KEY'),
    'Authorization': '2305843009488814713'
}


#xur's vendor hash: 2190858386
@bot.command()
async def whatisxur(ctx):
    if is_within_time_range():
        # user = DestinyUser(membership_id=4611686018483434245, membership_type=BungieMembershipType.TIGER_STEAM)
        # character = DestinyCharacter(membership_id=4611686018483434245, membership_type=BungieMembershipType.TIGER_STEAM, character_id=2305843009488814713)
        #print(dir(character))
        res = requests.get('https://www.bungie.net/Platform/Destiny2/Vendors/?components=402', headers = headers)
        
        if os.path.isfile(r".\vendors.json") == False:    
            with open('./vendors.json', 'w') as file:
                file.write(json.dumps(json.loads(res.text), indent = 4))
            with open('vendors.json', 'r') as file:
                data = json.load(file)
            
        item_hashes = []

        sales_data = data.get('Response', {}).get('sales', {}).get('data', {})

        for sale_id, sale_info in sales_data.items():
            sale_items = sale_info.get('saleItems', {})
            for item_id, item_info in sale_items.items():
                if 'itemHash' in item_info:
                    item_hashes.append(item_info['itemHash'])

        

        if os.path.isfile(r".\manifest.content") == False:
            get_manifest()
            all_data = build_dict(hashes)
            with open('manifest.pickle', 'wb') as data:
                pickle.dump(all_data, data)
                print("'manifest.pickle' created!\nDONE!")
        else:
            print('Pickle Exists')

        with open('manifest.pickle', 'rb') as data:
            all_data = pickle.load(data)
        #check if pickle exists, if not create one.
        item_list = []
        for item_hash in item_hashes:
            item = all_data['DestinyInventoryItemDefinition'][item_hash]
            item_list.append(item)
        # ghorn = all_data['DestinyInventoryItemDefinition'][hash]

        # for item in item_list:
        #     print('Name: '+item['displayProperties']['name'])
        #     print('Type: '+item['itemTypeDisplayName'])
        #     print('Flavor Text: '+item['flavorText'])
        quote = random.choice(quotes)
        embed = discord.Embed(title="__**Xûr's Wares**__", color=0x964B00)
        embed.add_field(name = "", value=f'*"{quote}"*', inline=False)
        for item in item_list:
            embed.add_field(name = f"__**{item['displayProperties']['name']}**__ --- {item['itemTypeDisplayName']}", value=f"*{item['flavorText']}*", inline=False)
        
            
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("I am currently unavailable. Please check back during the weekend.")

#Gjallarhorn
@bot.command()
async def whereisminerva(ctx):
    embed = discord.Embed(title="__**Incoming Transmission:**__", color=0x964B00)
    scraper = WebScraper("https://www.whereisminerva.com/")
    await ctx.send("Incoming transmission...")
    extracted_data = await scraper.fetch_minerva_data()
    embed.set_thumbnail(url="https://images.fallout.wiki/2/24/Atx_playericon_vaultboy_14.webp")
    embed.add_field(name = "", value=f"Good morning dwellers, and good morning America! Want to figure out how to build anything from a cattle prod to a nuclear reactor? Need to get rid of all that cumbersome gold bullion? Minerva's in town, and she's got you covered. Come pay a visit!", inline=False)
    embed.add_field(name = "", value=f"----------------------------------", inline=False)
    if extracted_data:
        for key, value in extracted_data.items():
            # bold the value
            key = f"__**{key}**__" if key else "" 
            embed.add_field(name=key, value=value, inline=False)
        embed.add_field(name = "", value=f"*And as always, stay safe America!*", inline=False)


    embed.add_field(name = "", value=f"----------------------------------", inline=False)
    

    embed.add_field(name = "", value = "This message has been sponsored by the people of the United States.", inline=False)
    embed.add_field(name = "", value = "__**Transmission End**__", inline=False)


    await ctx.send(embed=embed)

@bot.command()
async def whatisminerva(ctx):
    embed = discord.Embed(title="__**Minerva's Inventory**__", color=0x964B00)
    scraper = WebScraper("https://www.whereisminerva.com/")
    #until extracted data is available, send a loading message
    await ctx.send("Incoming transmission...")
    extracted_items = await scraper.fetch_minerva_inventory()
    extracted_costs = await scraper.fetch_minerva_costs()
    combined_data = []
    embed.set_thumbnail(url="https://images.fallout.wiki/2/24/Atx_playericon_vaultboy_14.webp")
    if extracted_items and extracted_costs:
        for item, cost in zip(extracted_items, extracted_costs):
            combined_data.append({'item':item, 'cost':cost})
        
        for element in combined_data:
            # print (f"{element['item']} for {element['cost']} bullion")
            # element = f"__**{element}**__" if element else "" 
            embed.add_field(name='', value=f"**{element['item']}** --- **{element['cost']} bullion**", inline=False)
        # print (value)
        # bold the value
        # print (key)
        # print (value)
        # value = f"__{value}__" if value else "" 
        # embed.add_field(name=value, value=, inline=False)
        embed.add_field(name = "", value=f"*And as always, stay safe America!*", inline=False)
    await ctx.send(embed=embed)
bot.run(os.getenv('TOKEN'))




