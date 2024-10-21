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

ansia_bot/  			~ root
├── admins.json 	~ contains the list of admins (to be filled)
├── core  				~ contains code utilities
│   ├── scraper.py  	~ handles updates and scraping of pads hosted on pad.poul.org
│   └── utils.py  		~ miscellanea of most function to handle data and text generation
├── data 				~ contains local copies of the traced pads
│   └── 
├── main.py 			~ send notifications to all traced chats when executed
├── main.sh  			~ used to execute main via a cronjob
├── padulati.json  		~ list of roles and people people to tag (to be filled) 
├── README.md  			~ this file
├── requirements.txt  	~ python dependecies 
├── request_handler.py	~ handler of the telegram interface 
└── settings.json		~ settings of the bot (to be filled)

## setup

In order to use the following bot follows these steps

### 0. Create a bot

Using @BotFather you can create a telegram bot. The open settings.json and add its unique token under the "token" key of the json.

If you are a memeber of POuL you can directly ask me the token of @poul_ansia_bot and skip this step.

### 1. Clone the repository

Clone the repository on your device move to your designated <base_directory> with the following command:
`git clone https://github.com/andreac01/ansia_bot.git`

### 2. Environment

In order to function out of the box it is assumed that the host has a properly configured virual environment. In order to do so run the following commands:

```
mkdir ~/venvs &&
cd ~/venvs &&
python -m venv telegram_venv &&
source ./telegram_venv/bin/activate &&
cd <base_directory>/ansia_bot &&
pip install -r requirements.txt
```

### 3. Run bot interface

After having configured the environment we can run the main interactive interface of the bot. To properly do so run the following commands:

```
nohup python update_helper.py &
```

nohup ensures that the program will run even after disconnection and & discards outputs.

### 4. Cron

To periodically execute the main function a crontab is needed. Run:
```
crontab -e
```
Then add this entry at the end of the file that will open
0 8 * * * <base_directory>/ansia_bot/main.sh

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
