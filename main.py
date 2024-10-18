import json
from datetime import datetime, timedelta
from core.utils import create_text, update_pads, create_text_undone
import telegram
import asyncio




async def main():
	# Load settings
	settings = json.load(open("settings.json"))
	bot = telegram.Bot(token=settings["token_bot"])
	text_today = settings["text_today"]
	text_tomorrow = settings["text_tomorrow"]
	parse_mode = settings["parse_mode"]
	chat_ids = settings["chat_ids"]
	urls = settings["urls"]

	# get dates
	today = datetime.now().strftime("%Y-%m-%d")
	tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

	# update pads
	update_pads(urls)
	# prepare text of today
	text = create_text(today, text_today) 
	if text != "":
		for chat_id in chat_ids:
			await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
	
	text2 = create_text(tomorrow, text_tomorrow)
	if text2 != "":
		for chat_id in chat_ids:
			await bot.send_message(chat_id=chat_id, text=text2, parse_mode=parse_mode)
	
	text3 = create_text_undone(today, settings["text_undone"])
	if text3 != "":
		for chat_id in chat_ids:
			await bot.send_message(chat_id=chat_id, text=text3, parse_mode=parse_mode)

		

if __name__ == "__main__":
    asyncio.run(main())