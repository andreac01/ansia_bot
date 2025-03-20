import json
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
	ApplicationBuilder,
	CommandHandler,
	ContextTypes,
	MessageHandler, 
	ConversationHandler, 
    filters, 
)
from core.scraper import scrape_pad, get_pad_title
from core.utils import create_text, update_pads, create_text_undone, escape_markdown, create_pad_text, create_links

with open("settings.json") as settings_file:
	settings = json.load(settings_file)
parse_mode = settings["parse_mode"]
# Define the conversation states
ASK_COURSE_NAME, ASK_COURSE_SITE_NAME, ASK_PADULATO, ASK_DATES, CREATE_PAD = range(5)

def clear_data_folder() -> None:
	"""Clears the data folder."""
	for file in os.listdir("data"):
		os.remove("data/" + file)


def get_paduli_text() -> str:
	"""Get the list of the paduled people.
	returns: markdown text with the paduled people
	"""
	padulati = json.load(open("padulati.json"))
	reply = "Currently paduled:\n"
	for group in padulati:
		reply += f"{escape_markdown(group)}: "
		for username in padulati[group]:
			reply += f" {escape_markdown(username)}"
		reply += "\n"
	return reply

def get_urls_text() -> str:
	"""Get the list of the active pads.
	returns: text with the active pads
	"""
	with open("settings.json") as settings_file:
		settings = json.load(settings_file)
	urls = settings["urls"]
	reply = "Currently active pads:\n"
	for url in urls:
		title = escape_markdown(get_pad_title(url))
		reply += f"{title}: {url}\n"
	return reply

def check_admin(update: Update) -> bool:
	"""Check if the user is an admin.
	args: update: telegram update
	returns: True if the user is an admin, False otherwise
	"""
	usernames = json.load(open("admins.json"))
	if update.message.from_user.username in usernames:
		return True
	else:
		return False

async def padula(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Padula a new person.
	args: update: telegram update
	context: telegram context
	returns: None"""
	padulati = json.load(open("padulati.json"))
	if not check_admin(update):
		await update.message.reply_text("You are not allowed to use this command", parse_mode=parse_mode)
		return
	text = update.message.text.replace("@", "")
	text = text.split(" ")
	if len(text) != 4:
		reply = "Usage: /padula padulo\\_type \\[old\\_paduled\\_username] \\[new\\_paduled\\_username]\n       to add or remove new paduli use the dummy user \'\\_\'\n\n"
		reply += get_paduli_text()
		await update.message.reply_text(reply, parse_mode=parse_mode)
		return
	else:
		group = text[1]
		old_username = text[2]
		new_username = text[3]
		flag = False
		if group not in padulati:
			padulati[group] = []
		if old_username in padulati[group]:
			padulati[group].remove(old_username)
			flag = True
			if new_username != "_":
				padulati[group].append(new_username)
			else:
				await update.message.reply_text(f"Succesfully removed {escape_markdown(old_username)}", parse_mode=parse_mode)
		if old_username == "_":
			if new_username in padulati[group]:
				await update.message.reply_text(f"{escape_markdown(new_username)} already paduled", parse_mode=parse_mode)
				return
			padulati[group].append(new_username)
			flag = True
		if flag:
			json.dump(padulati, open("padulati.json", "w"), indent=4)
			if new_username != "_":
				await update.message.reply_text(f"Succesfully paduled {escape_markdown(new_username)}", parse_mode=parse_mode)
		else:
			reply = f"Username {escape_markdown(old_username)} not found\n\n" + get_paduli_text()
			await update.message.reply_text(reply, parse_mode=parse_mode)

async def add_pad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Add a new pad.
	args: update: telegram update
	context: telegram context
	returns: None
	"""
	if not check_admin(update):
		await update.message.reply_text("You are not allowed to use this command", parse_mode=parse_mode)
		return
	text = update.message.text
	text = text.split(" ")
	if len(text) != 2:
		reply = "Usage: /add\\_pad \\[url\\_to\\_PUBLISHED\\_CodiMD]\n\n"
		reply += get_urls_text()
		await update.message.reply_text(reply, parse_mode=parse_mode)
		return
	else:
		url = text[1]
		try:
			scrape_pad(url)
		except Exception as e:
			await update.message.reply_text(f"Error: {escape_markdown(e)}\n\nTry to check the url", parse_mode=parse_mode)
			return
		with open("settings.json") as settings_file:
			settings = json.load(settings_file)
		urls = settings["urls"]
		urls.append(url)
		settings["urls"] = urls
		json.dump(settings, open("settings.json", "w"), indent=4)
		await update.message.reply_text("Pad added succesfully", parse_mode=parse_mode)

async def remove_pad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Remove a pad.
	args: update: telegram update
	context: telegram context
	returns: None
	"""
	if not check_admin(update):
		await update.message.reply_text("You are not allowed to use this command", parse_mode=parse_mode)
		return
	text = update.message.text
	text = text.split(" ")
	if len(text) != 2:
		reply = "Usage: /remove\\_pad \\[url\\_to\\_PUBLISHED\\_CodiMD]\n\n"
		reply += get_urls_text()
		await update.message.reply_text(reply, parse_mode=parse_mode)
		return
	else:
		url = text[1]
		with open("settings.json") as settings_file:
			settings = json.load(settings_file)
		urls = settings["urls"]
		if url in urls:
			urls.remove(url)
			settings["urls"] = urls
			json.dump(settings, open("settings.json", "w"), indent=4)
			clear_data_folder()
			update_pads(urls)
			await update.message.reply_text("Pad removed succesfully", parse_mode=parse_mode)
		else:
			reply = f"Url {url} not found\n\n" + get_urls_text()
			await update.message.reply_text(reply, parse_mode=parse_mode)

async def add_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Add current chat to the update list. Chat will receive updates daily updates from main.py function.
	args: update: telegram update
	context: telegram context
	returns: None
	"""
	if not check_admin(update):
		await update.message.reply_text("You are not allowed to use this command", parse_mode=parse_mode)
		return
	
	chatid = update.message.chat_id
	with open("settings.json") as settings_file:
		settings = json.load(settings_file)
	chat_ids = settings["chat_ids"]
	if chatid in chat_ids:
		await update.message.reply_text("Chat already added", parse_mode=parse_mode)
		return
	chat_ids.append(chatid)
	settings["chat_ids"] = chat_ids
	json.dump(settings, open("settings.json", "w"), indent=4)
	await update.message.reply_text("Chat added succesfully", parse_mode=parse_mode)

async def remove_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Remove a chat from the update list. Chat will not receive updates from main.py function.
	args: update: telegram update
	context: telegram context
	returns: None
	"""
	if not check_admin(update):
		await update.message.reply_text("You are not allowed to use this command", parse_mode=parse_mode)
		return
	chatid = update.message.chat_id
	with open("settings.json") as settings_file:
		settings = json.load(settings_file)
	chat_ids = settings["chat_ids"]
	if chatid in chat_ids:
		chat_ids.remove(chatid)
		settings["chat_ids"] = chat_ids
		json.dump(settings, open("settings.json", "w"), indent=4)
		await update.message.reply_text("Chat removed succesfully", parse_mode=parse_mode)
	else:
		await update.message.reply_text(f"Chatid {chatid} not found", parse_mode=parse_mode)

async def get_paduli(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Get the list of the paduled people.
	args: update: telegram update
	context: telegram context
	returns: None
	"""
	reply = get_paduli_text()
	await update.message.reply_text(reply, parse_mode=parse_mode)

async def get_pads(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Get the list of the active pads urls.
	args: update: telegram update
	context: telegram context
	returns: None
	"""
	reply = get_urls_text()
	await update.message.reply_text(reply, parse_mode=parse_mode)

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Add a new admin.
	args: update: telegram update
	context: telegram context
	returns: None
	"""
	if not check_admin(update):
		await update.message.reply_text("You are not allowed to use this command", parse_mode=parse_mode)
		return
	text = update.message.text.replace("@", "")
	text = text.split(" ")
	if len(text) != 2:
		await update.message.reply_text("Usage: /add\\_admin \\[tg\\_username]", parse_mode=parse_mode)
		return
	else:
		username = text[1]

		admins = json.load(open("admins.json"))
		if username in admins:
			await update.message.reply_text("User already admin", parse_mode=parse_mode)
			return
		admins.append(username)
		json.dump(admins, open("admins.json", "w"), indent=4)
		await update.message.reply_text("Admin added succesfully", parse_mode=parse_mode)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Check for tasks and send the messages to the chat_ids.
	args: update: telegram update
	context: telegram context
	returns: None
	"""
	# Load settings
	settings = json.load(open("settings.json"))
	text_undone = settings["text_undone"]
	text_today = settings["text_today"]
	text_tomorrow = settings["text_tomorrow"]
	parse_mode = settings["parse_mode"]
	urls = settings["urls"]
	# get dates
	today = datetime.now().strftime("%Y-%m-%d")
	tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

	# update pads
	update_pads(urls)
	# prepare text of today
	text = create_text(today, text_today, urls) + "\n\n\n\n" + create_text(tomorrow, text_tomorrow, urls) + "\n\n\n\n" + create_text_undone(today, text_undone, urls)
	if text == "\n\n\n\n\n\n\n\n":
		await update.message.reply_text("No pending tasks found", parse_mode=parse_mode)
		return
	await update.message.reply_text(text.replace("\n\n\n\n\n\n\n\n","\n\n\n\n"), parse_mode=parse_mode)

async def create_pad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Create a new pad. The conversation is divided in 4 steps: ask_course_name, ask_course_site_name, ask_dates, create_pad.
	args: update: telegram update
	context: telegram context
	returns: ASK_COURSE_NAME
	"""
	await update.message.reply_text("Welcome to the pad creation utility!\nWhat's the name of the course you are making the pad for?")
	return ASK_COURSE_NAME

async def ask_course_site_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Ask the short name of the course used in the website.
	args: update: telegram update
	context: telegram context
	returns: ASK_COURSE_SITE_NAME
	"""
	if update.message.text.lower().replace(" ", "").replace("\n", "") in ["cancel", "exit", "break"]:
		await update.message.reply_text("Operation cancelled")
		return ConversationHandler.END
	context.user_data['course_name'] = update.message.text
	await update.message.reply_text("Nice! \nWhat's the short name of the course used in the website?")
	return ASK_COURSE_SITE_NAME

async def ask_padulati(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Ask the tag of who got the padulo.
	args: update: telegram update
	context: telegram context
	returns: ASK_PADULATO
	"""
	if update.message.text.lower().replace(" ", "").replace("\n", "") in ["cancel", "exit", "break"]:
		await update.message.reply_text("Operation cancelled")
		return ConversationHandler.END
	context.user_data['course_site_name'] = update.message.text
	context.user_data['dates'] = []
	await update.message.reply_text(f"Perfect! \nWho is the lucky paduled guy?\nGive me its username so that I can tag him.")

	return ASK_PADULATO

async def ask_dates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Ask the dates of the course.
	args: update: telegram update
	context: telegram context
	returns: ASK_DATES
	"""
	if update.message.text.lower().replace(" ", "").replace("\n", "") in ["cancel", "exit", "break"]:
		await update.message.reply_text("Operation cancelled")
		return ConversationHandler.END
	
	if not update.message.text.startswith('@'):
		await update.message.reply_text("You need to tag the paduled guy (with '@'). Please try again")
		return ASK_PADULATO	

	context.user_data['padulato'] = update.message.text.replace("@", "")
	await update.message.reply_text(f"Great! Now let's add the dates of the course!\nPlease write the date of day {len(context.user_data['dates']) + 1} in the format YYYY MM DD. \nType done whe you have finished adding dates.")
	return ASK_DATES

async def get_all_dates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Get all the dates of the course.
	args: update: telegram update
	context: telegram context
	returns: ASK_DATES
	"""
	if update.message.text.lower().replace(" ", "").replace("\n", "") in ["cancel", "exit", "break"]:
		await update.message.reply_text("Operation cancelled")
		return ConversationHandler.END
	date = update.message.text
	if date.lower().replace(" ", "").replace("\n", "") == "done":
		if len(context.user_data['dates']) == 0:
			await update.message.reply_text("You need to add at least 1 date. Please try again")
			return ASK_DATES
		context.user_data['dates'] = sorted(context.user_data['dates'])
		informations = f"Course name: {context.user_data['course_name']}\nCourse site name: {context.user_data['course_site_name']}\nPadulato: {context.user_data['padulato']}\nDates:\n"
		for date in context.user_data['dates']:
			informations += f"   {date}\n"
		informations += "Is this information correct?"
		await update.message.reply_text(informations)
		return CREATE_PAD
	try:
		datetime.strptime(date, "%Y %m %d")
	except ValueError:
		await update.message.reply_text("Invalid date format, please try again")
		return ASK_DATES
	context.user_data['dates'].append(date)
	await update.message.reply_text(f"Got it! \nPlease write the date of day {len(context.user_data['dates']) + 1} in the format YYYY MM DD. \nType done whe you have finished adding dates.")
	return ASK_DATES

async def create_text_for_pad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Create the text for the pad.
	args: update: telegram update
	context: telegram context
	returns: ConversationHandler.END
	"""
	confirmations = ["yes", "y", "ok", "sure", "confirm", "correct", "giusto", "si", "sì", "yep"]

	padulati = json.load(open("padulati.json"))
	padulati["responsabile " + context.user_data['course_site_name']] = [context.user_data['padulato']]
	json.dump(padulati, open("padulati.json", "w"), indent=4)

	if update.message.text.lower().replace(" ", "").replace("\n", "") in confirmations:
		text = "*Markdown pad to load and publish as \"editable\" on pad.poul.org :*"
		await update.message.reply_text(text, parse_mode=parse_mode)
		for ids, date in enumerate(context.user_data['dates']):
			context.user_data['dates'][ids] = datetime.strptime(date, "%Y %m %d")
			
		text = create_pad_text(context.user_data['course_name'], context.user_data['course_site_name'], context.user_data['dates'])
		await update.message.reply_text(text)

		text = create_links(context.user_data['course_name'], context.user_data['course_site_name'], context.user_data['dates'])
		await update.message.reply_text(text)
	else:
		await update.message.reply_text("Please start again")
	return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Exit the conversation.
	args: update: telegram update
	context: telegram context
	returns: Conversation
	"""
	await update.message.reply_text("Operation cancelled")
	return ConversationHandler.END

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Get the help message.
	args: update: telegram update
	context: telegram context
	returns: None
	"""
	reply = "*Commands:*\n"
	reply += "/check: \n   check for tasks\n"
	reply += "/get\\_pads: \n   get the list of active pads\n"
	reply += "/create\\_pad: \n   create the markdown for a new pad and links for social\n"
	reply += "/add\\_pad \\[url\\_to\\_PUBLISHED\\_CodiMD]: \n   adds a new pad (admin required)\n"
	reply += "/remove\\_pad \\[url\\_to\\_PUBLISHED\\_CodiMD]: \n   removes a pad (admin required)\n"
	reply += "/get\\_paduli: \n   get the list of paduled people\n"
	reply += "/padula padulo\\_type \\[old\\_paduled\\_username] \\[new\\_paduled\\_username]: \n   padules a new person (admin required)\n"
	reply += "/add\\_chat: \n   add current chat id to update list\n"
	reply += "/remove\\_chat: \n   removes current chat id from update list (admin required)\n"
	reply += "/add\\_admin \\[tg\\_username]: \n   adds a new admin (admin required)\n"
	reply += "/help: \n   get this message\n"


	await update.message.reply_text(reply, parse_mode=parse_mode)




def main():
	# Load settings from a JSON file
	with open("settings.json") as settings_file:
		settings = json.load(settings_file)

	token = settings["token"]

	# Create the application
	app = ApplicationBuilder().token(token).build()
	
	# Add command handlers
	app.add_handler(CommandHandler("start", help))
	app.add_handler(CommandHandler("padula", padula))
	app.add_handler(CommandHandler("help", help))
	app.add_handler(CommandHandler("add_pad", add_pad))
	app.add_handler(CommandHandler("remove_pad", remove_pad))
	app.add_handler(CommandHandler("add_chat", add_chat))
	app.add_handler(CommandHandler("remove_chat", remove_chat))
	app.add_handler(CommandHandler("get_paduli", get_paduli))
	app.add_handler(CommandHandler("get_pads", get_pads))
	app.add_handler(CommandHandler("add_admin", add_admin))
	app.add_handler(CommandHandler("check", check))
	app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('create_pad', create_pad)],
        states={
            ASK_COURSE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_course_site_name)],
			ASK_COURSE_SITE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_padulati)],
			ASK_PADULATO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_dates)],
			ASK_DATES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_all_dates)],
			CREATE_PAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_text_for_pad)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))

	
	# Debug time
	print(f"Request handler function started at {datetime.now()}")

	# Start polling for updates
	app.run_polling()

# Check if an event loop is already running
if __name__ == "__main__":
	main()
