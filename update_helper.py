import json
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
	ApplicationBuilder,
	CommandHandler,
	ContextTypes,
)
from core.scraper import scrape_pads, get_pad_title
from core.utils import create_text, update_pads

with open("settings.json") as settings_file:
	settings = json.load(settings_file)
parse_mode = settings["parse_mode"]

def clear_data_folder():
	for file in os.listdir("data"):
		os.remove("data/" + file)

def escape_markdown(text: str) -> str:
    escape_chars = r'_[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def get_paduli_text():
	padulati = json.load(open("padulati.json"))
	reply = "Currently paduled:\n"
	for group in padulati:
		reply += f"{escape_markdown(group)}: "
		for username in padulati[group]:
			reply += f" {escape_markdown(username)}"
		reply += "\n"
	return reply

def get_urls_text():
	with open("settings.json") as settings_file:
		settings = json.load(settings_file)
	urls = settings["urls"]
	reply = "Currently active pads:\n"
	for url in urls:
		title = escape_markdown(get_pad_title(url))
		reply += f"{title}: {url}\n"
	return reply

def check_admin(update: Update) -> bool:
	usernames = json.load(open("allowed_users.json"))
	if update.message.from_user.username in usernames:
		return True
	else:
		return False

async def padula(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
			if new_username != "_":
				padulati[group].append(new_username)
				flag = True
			else:
				await update.message.reply_text(f"Succesfully removed {escape_markdown(old_username)}", parse_mode=parse_mode)
		if old_username == "_":
			padulati[group].append(new_username)
			flag = True
		if flag:
			json.dump(padulati, open("padulati.json", "w"))
			await update.message.reply_text(f"Succesfully paduled {escape_markdown(new_username)}", parse_mode=parse_mode)
		else:
			reply = f"Username {escape_markdown(old_username)} not found\n\n" + get_paduli_text()
			await update.message.reply_text(reply, parse_mode=parse_mode)

async def add_pad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
			scrape_pads(url)
		except Exception as e:
			await update.message.reply_text(f"Error: {escape_markdown(e)}\n\nTry to check the url", parse_mode=parse_mode)
			return
		with open("settings.json") as settings_file:
			settings = json.load(settings_file)
		urls = settings["urls"]
		urls.append(url)
		settings["urls"] = urls
		json.dump(settings, open("settings.json", "w"))
		await update.message.reply_text("Pad added succesfully", parse_mode=parse_mode)

async def remove_pad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
			json.dump(settings, open("settings.json", "w"))
			clear_data_folder()
			update_pads(urls)
			await update.message.reply_text("Pad removed succesfully", parse_mode=parse_mode)
		else:
			reply = f"Url {url} not found\n\n" + get_urls_text()
			await update.message.reply_text(reply, parse_mode=parse_mode)

async def add_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
	json.dump(settings, open("settings.json", "w"))
	await update.message.reply_text("Chat added succesfully", parse_mode=parse_mode)

async def remove_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
		json.dump(settings, open("settings.json", "w"))
		await update.message.reply_text("Chat removed succesfully", parse_mode=parse_mode)
	else:
		await update.message.reply_text(f"Chatid {chatid} not found", parse_mode=parse_mode)

async def get_paduli(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	reply = get_paduli_text()
	await update.message.reply_text(reply, parse_mode=parse_mode)

async def get_pads(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	reply = get_urls_text()
	await update.message.reply_text(reply, parse_mode=parse_mode)

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

		admins = json.load(open("allowed_users.json"))
		admins.append(username)
		json.dump(admins, open("allowed_users.json", "w"))
		await update.message.reply_text("Admin added succesfully", parse_mode=parse_mode)

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	cur_chatid = update.message.chat_id
	cur_userid = update.message.from_user.id
	reply = f"Chat id: {cur_chatid}\nUser id: {cur_userid}"
	await update.message.reply_text(reply, parse_mode=parse_mode)


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	# Load settings
	settings = json.load(open("settings.json"))
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
	text = create_text(today, text_today) + "\n\n" + create_text(tomorrow, text_tomorrow)
	if text == "\n\n":
		await update.message.reply_text("No pending tasks found", parse_mode=parse_mode)
		return
	await update.message.reply_text(text, parse_mode=parse_mode)
		

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	reply = "Commands:\n\n"
	reply += "/check: \n   check for tasks\n"
	reply += "/get\\_pads: \n   get the list of active pads\n"
	reply += "/add\\_pad \\[url\\_to\\_PUBLISHED\\_CodiMD]: \n   adds a new pad (admin required)\n"
	reply += "/remove\\_pad \\[url\\_to\\_PUBLISHED\\_CodiMD]: \n   removes a pad (admin required)\n"
	reply += "/get\\_paduli: \n   get the list of paduled people\n"
	reply += "/padula padulo\\_type \\[old\\_paduled\\_username] \\[new\\_paduled\\_username]: \n   padules a new person (admin required)\n"
	reply += "/add\\_chat: \n   add current chat id to update list\n"
	reply += "/remove\\_chat: \n   removes current chat id from update list (admin required)\n"
	reply += "/add\\_admin \\[tg\\_username]: \n   adds a new admin (admin required)\n"
	reply += "/info: \n   get info about the current chat id and user id\n"
	reply += "/help: \n   get this message\n"
	reply += "/start: \n   get this message\n"


	await update.message.reply_text(reply, parse_mode=parse_mode)

def main():
	# Load settings from a JSON file
	with open("settings.json") as settings_file:
		settings = json.load(settings_file)

	token = settings["token_bot"]

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
	app.add_handler(CommandHandler("info", info))

	
	print("Handlers added")
	
	# Start polling for updates
	app.run_polling()

# Check if an event loop is already running
if __name__ == "__main__":
	main()
