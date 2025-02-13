# Ansia Bot

## Description

A simple bot to handle pads and notify people of deadlines.
The bot is available at https://t.me/poul_ansia_bot
The bot is used by Politecnico Open unix Labs student association to handle deadlines related to courses.

The code is divided into two parts:
- main.py: This script should be executed periodically in order to automatically sends notification with upcoming and missed deadlines. 
- request_handler.py: This script handles all interactions with the bot, mainly aimed at adding admins, chats, pads or visualizing the current settings.

## Commands

 - /check:  check for tasks
 - /get_pads:  get the list of active pads
 - /create_pad:  create the markdown for a new pad and links for social
 - /add_pad [url_to_PUBLISHED_CodiMD]:  adds a new pad (admin required)
 - /remove_pad [url_to_PUBLISHED_CodiMD]:  removes a pad (admin required)
 - /get_paduli:  get the list of paduled people
 - /padula padulo_type [old_paduled_username] [new_paduled_username]:  padules a new person (admin required)
 - /add_chat:  add current chat id to update list
 - /remove_chat:  removes current chat id from update list (admin required)
 - /add_admin [tg_username]:  adds a new admin (admin required)
 - /info:  get info about the current chat id and user id
 - /help:  get this message
 - /start:  get this message

## Files organization

ansia_bot/  			~ root <br>
├── admins.json 	~ contains the list of admins (to be filled)  <br>
├── core  				~ contains code utilities <br>
│   ├── scraper.py  	~ handles updates and scraping of pads hosted on pad.poul.org <br>
│   └── utils.py  		~ miscellanea of most function to handle data and text generation <br>
├── data 				~ contains local copies of the traced pads <br>
│   └──  <br>
├── main.py 			~ send notifications to all traced chats when executed <br>
├── main.sh  			~ used to execute main via a cronjob <br>
├── padulati.json  		~ list of roles and people people to tag (to be filled) <br> 
├── README.md  			~ this file <br>
├── requirements.txt  	~ python dependecies  <br>
├── request_handler.py	~ handler of the telegram interface  <br>
└── settings.json		~ settings of the bot (to be filled) <br>

## setup

In order to use the following bot follows these steps

### 0. Create a bot

Using @BotFather you can create a telegram bot. The open settings.json and add its unique token under the "token" key of the json.

If you are a memeber of POuL you can directly ask me the token of @poul_ansia_bot and skip this step.

### 1. Clone the repository

Clone the repository on your device move to your designated <base_directory> with the following command:

`git clone https://github.com/andreac01/ansia_bot.git`

In settings.json you should place your bot token. 

In main.sh you should properly set <base_directory>

### 2. Environment

In order to function out of the box it is assumed that the host has a properly configured virual environment. In order to do so run the following commands:

```
mkdir ~/venvs &&
cd ~/venvs &&
python3 -m venv telegram_venv &&
source ./telegram_venv/bin/activate &&
cd <base_directory>/ansia_bot &&
pip install -r requirements.txt
```

Remember to change <base_directory> properly

### 3. Run bot interface

#### 3.a plain implementation

After having configured the environment we can run the main interactive interface of the bot. To properly do so run the following commands:

```
nohup python3 request_handler.py &
```

nohup ensures that the program will run even after disconnection and & discards outputs.

#### 3.b daily check for changes on repository
To periodically pull from the github repository any change. Run:
```
crontab -e
```
Then add this entry at the end of the file that will open

`0 4 * * * <base_directory>/ansia_bot/auto_update.sh`

Remember to change <base_directory> properly

### 4. Daily update message

To periodically execute the main function a crontab is needed. Run:
```
crontab -e
```
Then add this entry at the end of the file that will open

`0 8 * * * <base_directory>/ansia_bot/main.sh`

Remember to change <base_directory> properly

### 5. Padula and set admins

First of all you will need to add yourself as an admin. To do so add your username to the admins.json file.

All later modifications can be done through the telegra interface of the bot.

## Remember to:

1. Add the token in settings.json (via editor)
2. Add admins in admins.json (via telegram)
3. Add direttivo and social representatives in padulati.json (via telegram)
4. Add the chat you want to update using (via telegram)
5. Add all the pads (via telegram)
6. Always publish the pads and create them as editable (via pad.poul.org)


## Implementation notes:

The code is divided into two main parts: 
- request_handler.py: handles all interactions with the bot, mainly aimed at adding admins, chats, pads or visualizing the current settings.
- main.py: sends notifications to all traced chats (automatic notification)

Additionally there are the two folders:
- core: contains code utilities:
  - scraper.py: handles updates and scraping of pads hosted on pad.poul.org and added via the telegram bot interface
  - utils.py: miscellanea of most function to handle data and text generation. Here are all general functions that are used to parse the pad for particular informations.
- data: a folder containing local copies of the traced pads. Old pads are automatically deleted, while new pads are added by the scraper once they are added to the list of pads to be traced.
  
Finally there are the json files used to store settings or informations:
- admins.json: contains the list of admins that are user that can add the bot to chat and add new pads
- padulati.json: contains the list of roles and people people to tag
- settings.json: contains some settings of the bot, such as the token of the bot and the list of chats to update
