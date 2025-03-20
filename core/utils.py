from __future__ import generators
import re
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))
from scraper import scrape_pad, get_pad_title
from datetime import timedelta

class MissingTagException(Exception):
	"""Exception raised when a tag is missing in the recipients file."""
	def __init__(self, missing_tags):
		self.missing_tags = missing_tags
		self.message = f"Missing tags: {missing_tags}"
		super().__init__(self.message)

def escape_markdown(text: str) -> str:
	"""Escape all markdown special characters found in text.
	args: tetx: text to escape
	returns: escaped text
	"""
	escape_chars = r'_[]()~`>#+-=|{}.!'
	return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def mach_dates(text: str) -> list:
	"""matches dates in the format - (YYYY-MM-DD) in text.
	args: text: text to search for dates
	returns: list of dates in the format YYYY-MM-DD
	"""
	matches = re.findall(r"- \((\d{4})-(\d{2})-(\d{2})\)", text)
	return ["{}-{}-{}".format(year, month, day) for year, month, day in matches]


def find_tasks(text:str, return_done=False):
	"""Finds tasks in the format - [ ] in text.
	args: text: text to search for tasks
	returns: list of tasks
	"""
	pattern = re.compile(r"\s*- \[")
	for line in text.split("\n"):
		if pattern.match(line):
			if return_done:
				yield line
			elif not line.startswith(" " * line.index("- [") + "- [x]"):
				yield line

def substitute_recipients(text: str, recipients_file="padulati.json") -> str:
	"""Substitute recipients in the format **_recipient_** with the corresponding usernames.
	args: text: text to substitute recipients in
	recipients_file: file containing the recipients usernames
	returns: text with recipients substituted
	"""
	with open(recipients_file) as f:
		recipients = json.load(f)

	for recipient in recipients:
		tags = ""
		for username in recipients[recipient]:
			tags += f"@{escape_markdown(username)} "
		if tags == "":
			tags = " "
		
		text = text.replace("**_" + recipient + "_**", tags[:-1])
	return text

def find_tasks_and_dates(text: str, return_done=False) -> dict:
	"""Finds tasks and dates in the format - (YYYY-MM-DD) in text.
	args: text: text to search for tasks and dates
	returns: dictionary with dates as keys and tasks as values
	"""
	date_to_task = {}
	text = substitute_recipients(text)

	dates = mach_dates(text)
	for idx, date in enumerate(dates):

		cur_date_text_array = text.split(dates[idx])
		if len(cur_date_text_array) == 2:
			cur_date_text = cur_date_text_array[1]
		else:
			count = len([x for x in dates[:idx] if x == dates[idx]])
			cur_date_text = cur_date_text_array[count + 1]
		if idx != len(dates) - 1:
			cur_date_text = cur_date_text.split(dates[idx + 1])[0]
		tasks = find_tasks(cur_date_text, return_done)

		if tasks:
			if date_to_task.get(date, None) == None:
				date_to_task[date] = list(tasks)
			else:
				date_to_task[date] += list(tasks)
	return date_to_task

def create_text(date: str, base_text: str, urls: list) -> str:
	"""Creates a text with the tasks of the day.
	args: date: date to search for tasks
	base_text: text to append the tasks to
	returns: markdown text with the tasks of the day
	"""

	text = base_text
	data_files = os.listdir("data")
	texts = {}
	for file in data_files:
		with open("data/" + file, "r") as f:
			course_description = f.read()
			f.close()
			tasks_and_dates = find_tasks_and_dates(course_description)
			for deadline in tasks_and_dates:
				if date == deadline:
					tasks = list(tasks_and_dates[deadline])
					if texts.get(file, None) == None and len(tasks) > 0:
						for url in urls:
							if file.split('.')[0] == get_pad_title(url):
								texts[file] = "\n\n*" + file.split('.')[0].replace("_", " ") + "* [link 🔗](" + url + ")"
					for task in tasks:
						texts[file] += "\n\n" + task.replace("- [ ]", "\u2757")
	for key in texts:
		text += texts[key]
	if text == base_text:
		return ""
	return text

def create_text_undone(date: str, base_text: str, urls: list) -> str:
	"""Creates a text with the task that were not completed before date.
	args: date: last date to search for tasks
	base_text: text to append the tasks to
	returns: markdown text with the undone tasks
	"""
	text = base_text
	data_files = os.listdir("data")
	texts = {}
	for file in data_files:
		with open("data/" + file, "r") as f:
			course_description = f.read()
			f.close()
			tasks_and_dates = find_tasks_and_dates(course_description)
			for deadline in tasks_and_dates:
				if date > deadline:
					tasks = list(tasks_and_dates[deadline])
					if texts.get(file, None) == None and len(tasks) > 0:
						for url in urls:
							if file.split('.')[0] == get_pad_title(url):
								texts[file] = "\n\n*" + file.split('.')[0].replace("_", " ") + "* [link 🔗](" + url + ")"
					for task in tasks:
						texts[file] += "\n\n" + task.replace("- [ ]", "\u2757")

	for key in texts:
		text += texts[key]
	if text == base_text:
		return ""
	return text

def update_pads(urls: list, relative_path="../data") -> None:
	"""Updates the pads with the latest information. By scraping the data from the urls.
	args: urls: list of urls to scrape
	"""
	data_dir = os.path.join(os.path.dirname(__file__), relative_path)
	for file in os.listdir(data_dir):
		os.remove(data_dir + "/" + file)
	for url in urls:
		scrape_pad(url, relative_path)

def create_pad_text(course_name: str, site_name:str, days: list) -> str:
	"""Creates a text with the tasks for the course.
	args: course_name: name of the course
	site_name: short name of the course used in the website url
	days: list of dates
	returns: markdown text with the tasks for the course
	"""

	day_1 = days[0]

	day_before = day_1 - timedelta(days=1)
	week_before = day_1 - timedelta(days=7)
	two_weeks_bef = day_1 - timedelta(days=14)
	three_weeks_bef = day_1 - timedelta(days=21)
	month_before = day_1 - timedelta(days=28)
	month_and_half_bef = day_1 - timedelta(days=42)

	if ((day_1 - timedelta(days=7)).day < 8):
		day_tamtam = (day_1 - timedelta(days=20))
		day_tamtam = day_tamtam.replace(day=25)
	else: 
		day_tamtam = day_1.replace(day=8)

	text = f"""# Corso {course_name}

	### TODO: 
	- ({month_and_half_bef.strftime("%Y-%m-%d")})
	 		- [ ] Elaborare proposte definitive delle date del corso (**_responsabile{site_name}_**)(**_direttivo_**) riceve e comunica a gruppo social
			- [ ] Mandare mail a Poli per chiedere aule (**_direttivo_**) 
				- Verificare necessità particolari come capienza/prese elettriche 
				- Mail a eventileonardo@polimi.it o eventibovisa@polimi.it
				- Dopo una settimana, senza risposta, solleciti telefonici fatti a Lorella Errico e Francesco Esposito (Lorella è stata più efficiente) (In generale cercare in rubrica: area infrastrutture e servizi - funzioni di staff)
			- [ ] Creare pagina dell'edizione sul sito + creare messaggio con i link analytics (e lo short URL) + form di iscrizione (**_social_**)
				- Nella descrizione va specificato: il link del form, se registriamo/streammiamo, dove trovare il link dello stream/rec, in che lingua è il talk, eventuali prerequisiti (anche cose da installare)"
	- ({month_before.strftime("%Y-%m-%d")}) 
			- [ ] Verificare prenotazione aule sui servizi online (**_social_**)
				- Se non ci sono aule prenotate, sollecitare il poli (**_direttivo_**) (molto urgente)
			- [ ] Deadline per presentare sui gruppi la bozza del manifesto (**_designers_**) (sia su gruppo manifesti che su gruppo del corso {site_name})
			- [ ] Aggiornare pagina sul sito con aule (**_social_**)
	- ({day_tamtam.strftime("%Y-%m-%d")}) 
			- [ ] compilare PoliTamTam (**_direttivo_**)
	- ({three_weeks_bef.strftime("%Y-%m-%d")}) 
			- [ ] Mandare in approvazione manifesto (**_direttivo_**)
			- [ ] Deadline manifesto completo con footer (**_social_**) (**_designers_**) (**_direttivo_**)
	- ({two_weeks_bef.strftime("%Y-%m-%d")}) 
			- [ ] Stampare manifesti e appenderli (**_social_**)
	- ({week_before.strftime("%Y-%m-%d")}) 
			- [ ] Aggiungere orari e aule al manifesto approvato (**_designers_**)
			- [ ] Posts IG+TG con manifesto del corso (**_social_**)
			- [ ] Deadline design thumbnails youtube (**_designers_**)
			- [ ] Schedulare live (**_social_**)
			- [ ] Schedule posts telegram (12:00 del giorno del corso) (**_social_**)
	- ({day_before.strftime("%Y-%m-%d")}) 
			- [ ] Pubblicare storia IG: "ci vediamo domani" (**_social_**)
		"""
	for day in days:
		text += f"""
		- ({day.strftime("%Y-%m-%d")}) 
				- [ ] 12:00 Pubblicare storia IG: promemoria corso (**_social_**)"""

	return text

def create_links(course_name: str, short_name: str, dates: list) -> str:
	"""Creates links for the course.
	args: course_name: name of the course
	short_name: short name of the course used in the website url
	dates: list of dates
	returns: links for the course
	"""
	year = dates[0].year
	links = f"""Link per {course_name}:
	Link da mettere nel QR: https://poul.org/courses/{short_name}/?mtm_campaign={short_name}{year}&mtm_kwd=manifesto
	Link short per il manifesto: go.poul.org/{short_name}{year}
	Link da mettere nel TamTam: https://poul.org/courses/{short_name}/?mtm_campaign={short_name}{year}&mtm_kwd=tamtam
	Link da usare su telegram: https://poul.org/courses/{short_name}/?mtm_campaign={short_name}{year}&mtm_kwd=tg
	Link da usare su instagram: https://poul.org/courses/{short_name}/?mtm_campaign={short_name}{year}&mtm_kwd=ig
	Link base: https://poul.org/courses/{short_name}/
	"""
	return links

