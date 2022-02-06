# mhrise_discord_hunter_bot.py

import os
import json

# this loads the discord library
import discord
from dotenv import load_dotenv
from discord.ext.commands import Bot

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BOT_ID = int(os.getenv('DISCORD_BOT_ID'))

# allows for bot to detect all members belonging to the server.

intents = discord.Intents.default()
intents.members = True
intents.members = True
intents.reactions = True
intents.messages = True

# Client is an object that represents a connection to Discord.
# This handles events, tracks state and interacts with discord APIs
client = discord.Client(intents=intents)
bot_prefix = 'mhr.'
bot = Bot(command_prefix=bot_prefix.lower())

# get the server for Catwad
localServer = discord.utils.get(client.guilds, id=GUILD)


@bot.command(name='item')
async def on_message(search_message):
    # Don't accept any messages from the bot itself
    if search_message.author.id == BOT_ID:
        return
    print('~~~~~~~\nStart of search command logging.\n')
    # return the message sent by the user
    search_term = search_message.message.content

    # trim the command request to leave only the search term
    search_term = search_term.replace("mhr.item", "")

    # strip spaces
    search_term = search_term.strip()

    # load in the db
    with open(r'mhr_test_db.json') as fp:
        mhr_item_db = json.loads(fp.read())

    # debugging lines
    # print('db loaded successfully, sample data print')
    # print('Format for one item entry: ', mhr_item_db['item_entry'][126])
    # print('Item name format : ', mhr_item_db['item_entry'][126]['item_name'])
    # print('Number of entries:', len(mhr_item_db['item_entry']))
    # print('Search term provided is:', search_term)
    # print('Format for monster drop list: ', len(mhr_item_db['item_entry'][126]['item_details_page'][0]['drop_list']))
    # print('Format for quest drop list:', mhr_item_db['item_entry'][190]['item_details_page'][0]['quest_rewards'][0])
    # print('Checking if there are both monster items and quest rewards: ', len(mhr_item_db['item_entry'][190]['item_details_page'][0]))
    # print('Debugging - expecting to print item name. ', mhr_item_db['item_entry'][0]['item_name'].lower())

    # Define all the inputs to be used in the embed.
    monster_result = ''
    previous_monster_result = ''
    method_result = ''
    monster_rate_amount_result = ''

    item_type = ''

    quest_result = ''
    previous_quest_result = ''
    quest_rate_amount_result = ''

    item_match_flag = ''
    monster_drop_flag = ''
    quest_reward_flag = ''

    print('Database read successfully. Initiating search loop, with search term "', search_term, '".')
    # begin matching
    for item in mhr_item_db['item_list']:
        # for loop will continue to iterate past the end of the loop, add a check to break the loop if list reached
        # the end
        print('Attempting to match "', search_term, '" with ', item['item_name'], '...')
        if not item:
            print('End of list reached with no matches.')
            break

        try:
            # once a match is found, extract the relevant info

            if item['item_name'].lower() == search_term.lower():
                print('An item was found. Entry is as follows:\n', item, "\n")
                item_match_flag = True
                # write the embed title in case users don't enter the correct search term
                embed_title = item['item_name']

                item_link_URL = item['item_URL']
                item_image_URL = item['item_avatar']
                item_description = item['item_description']

                # Match the item type to the consumable type.

                if int(item['item_type']) == 0:
                    item_type = "Consumable"

                print('Attempting to find monster drop data...')

                # checks if monster drop is present
                if "monster_items" not in item:
                    print('No monster drop data found.\n')
                    monster_result = "N/A"
                    method_result = "N/A"
                    monster_rate_amount_result = "N/A"
                    monster_drop_flag = False

                # once monster drop list is found, iterate through the list and append to a string
                else:
                    print('Monster drop data found.')
                    for item_source in item['monster_items']:
                        # define current result
                        current_monster_result = item_source['rank'] + ' ' + item_source['monster']

                        if current_monster_result == previous_monster_result:
                            monster_result = monster_result + '" "' + '\n'
                        else:
                            monster_result = monster_result + item_source['rank'] + ' ' + item_source['monster'] + '\n'
                        method_result = method_result + item_source['method'] + '\n'
                        monster_rate_amount_result = monster_rate_amount_result + item_source['amount'] + ' ' + \
                                                     item_source['rate'] + '\n'
                        # to save on characters, note down previous result
                        previous_monster_result = item_source['rank'] + ' ' + item_source['monster']

                print('Attempting to find quest reward data...')
                # checks if quest rewards are present
                if "quest_rewards" not in item:
                    print('No reward data found.\n')
                    quest_result = 'N/A'
                    quest_rate_amount_result = 'N/A'
                    quest_reward_flag = False

                else:
                    print('Quest reward data found.')
                    for quest_source in item['quest_rewards']:
                        print(quest_source)
                        quest_name_reformatted = quest_source['quest_name'].replace("â˜…", "★")
                        current_quest_result = quest_name_reformatted
                        if current_quest_result == previous_quest_result:
                            quest_result = quest_result + '" "' + '\n'
                        else:
                            # this code is for having hyperlinks quest_result = quest_result + "[" +
                            # quest_name_reformatted + "](" + quest_source['quest_url'] + ")\n"
                            quest_result = quest_result + quest_name_reformatted + "\n"

                        quest_rate_amount_result = quest_rate_amount_result + quest_source['amount'] + ' ' + \
                                                   quest_source['rate'] + '\n'
                        previous_quest_result = quest_source['quest_name']

                if monster_drop_flag is False and quest_reward_flag is False:
                    print('No relevant data found, skip to embed creation.')
                    break

                print('break the loop to prevent further searching')

                break
            else:
                item_match_flag = False
        except KeyError:
            pass

    if not item_match_flag:
        await search_message.channel.send("I couldn't find any items matching that search, please try again.")
    else:
        print('-- Final data inputs ---')
        print('monster result:', monster_result)
        print('method result:', method_result)
        print('rate:', monster_rate_amount_result)
        print('\nquest name:', quest_result)
        print('rate:', quest_rate_amount_result)

        # define the embed
        search_result_embed = discord.Embed(title=embed_title,
                                            description="[Kiranico](" + item_link_URL + ")\n\n" +
                                                        "**Item Type**: " + item_type + "\n" +
                                                        "*" + item_description + "*")
        search_result_embed.set_thumbnail(url=item_image_URL)
        search_result_embed.add_field(name="----------------\nMonster Items\n----------------",
                                      value="o", inline=False)
        search_result_embed.add_field(name="Monster", value=monster_result, inline=True)
        search_result_embed.add_field(name="Method", value=method_result, inline=True)
        search_result_embed.add_field(name="Rate/Amount", value=monster_rate_amount_result, inline=True)

        search_result_embed.add_field(name="----------------\nQuest Rewards\n----------------",
                                      value="o", inline=False)
        search_result_embed.add_field(name="Quest", value=quest_result, inline=True)
        search_result_embed.add_field(name="Rate/Amount", value=quest_rate_amount_result, inline=True)

        await search_message.channel.send(embed=search_result_embed)
        print('Search results provided, ending log.\n~~~~~~~\n')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord.')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="mewsic~"))
    print("Bot status has been changed to list the bot help command!\n")


bot.run(TOKEN)
# # client.run(TOKEN)
