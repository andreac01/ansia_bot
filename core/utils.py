from __future__ import generators
import re
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))
from scraper import scrape_pads
from datetime import date, timedelta

def match_next_date(text):
    """(yyyy-mm-dd)"""
    return re.search(r"(\d{4})-(\d{2})-(\d{2})", text)

def escape_markdown(text: str) -> str:
    escape_chars = r'_[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def mach_dates(text):
    """- (yyyy-mm-dd)"""
    matches = re.findall(r"- \((\d{4})-(\d{2})-(\d{2})\)", text)
    return ["{}-{}-{}".format(year, month, day) for year, month, day in matches]


def find_tasks(text, return_done=False):
    """- [ ]"""
    pattern = re.compile(r"\s*- \[")
    for line in text.split("\n"):
        if pattern.match(line):
            if return_done:
                yield line
            elif not line.startswith(" " * line.index("- [") + "- [x]"):
                yield line

def substitute_recipients(text, recipients_file="padulati.json"):
    """(**_direttivo_**) to @direttivo"""
    with open(recipients_file) as f:
        recipients = json.load(f)

    for recipient in recipients:
        tags = ""
        for username in recipients[recipient]:
            tags += f"@{username} "
        if tags == "":
            tags = " "
        
        text = text.replace("*_" + recipient + "_*", tags[:-1])
    return text

def find_tasks_and_dates(text, return_done=False):
    date_to_task = {}
    text = substitute_recipients(text)

    dates = mach_dates(text)
    for idx, date in enumerate(dates):

        cur_date_text = text.split(dates[idx])[1]
        if idx != len(dates) - 1:
            cur_date_text = cur_date_text.split(dates[idx + 1])[0]
        tasks = find_tasks(cur_date_text, return_done)

        if tasks:
            date_to_task[date] = tasks
    return date_to_task

def create_text(date, base_text):
	text = base_text
	data_files = os.listdir("data")
	for file in data_files:
		with open("data/" + file, "r") as f:
			print(f"Reading {file}")
			course_description = f.read()
			f.close()
			tasks_and_dates = find_tasks_and_dates(course_description)
			for deadline in tasks_and_dates:
				if date == deadline:
					for task in tasks_and_dates[deadline]:
						text += "\n\n" + file.split('.')[0] + "\n" + task.replace("- [ ]", "\u2757")
					print("Adding tasks")
			print("Done")
	print()
	if text == base_text:
		return ""
	return text

def create_text_undone(date, base_text):
	text = base_text
	data_files = os.listdir("data")
	for file in data_files:
		with open("data/" + file, "r") as f:
			print(f"Reading {file}")
			course_description = f.read()
			f.close()
			tasks_and_dates = find_tasks_and_dates(course_description)
			for deadline in tasks_and_dates:
				if date > deadline:
					for task in tasks_and_dates[deadline]:
						text += "\n\n" + escape_markdown(file.split('.')[0]) + "\n" + task.replace("- [ ]", "\u2757")
					print("Adding tasks")
			print("Done")
	print()
	if text == base_text:
		return ""
	return text

def update_pads(urls):
	for url in urls:
		print(f"Scraping {url}")
		scrape_pads(url)
		print("Done")

def create_pad_text(course_name: str, site_name:str, days: list):
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
	- ({month_and_half_bef}) - Elaborare proposte definitive delle date del corso (_responsabile corso_)(**_direttivo_** riceve e comunica a gruppo social (taggando responsabile gruppo social))
			- [ ] Mandare mail a Poli per chiedere aule (**_direttivo_**) 
				- Verificare necessità particolari come capienza/prese elettriche 
				- Mail a eventileonardo@polimi.it o eventibovisa@polimi.it
				- Dopo una settimana, senza risposta, solleciti telefonici fatti a Lorella Errico e Francesco Esposito (Lorella è stata più efficiente) (In generale cercare in rubrica: area infrastrutture e servizi - funzioni di staff)
			- [ ] Creare pagina dell'edizione sul sito + creare messaggio con i link analytics (e lo short URL) + form di iscrizione (**_social_**)
				- Nella descrizione va specificato: il link del form, se registriamo/streammiamo, dove trovare il link dello stream/rec, in che lingua è il talk, eventuali prerequisiti (anche cose da installare)"
		- ({month_before}) Ottenere aule dal Poli (**_direttivo_**)
			- [ ] Deadline manifesto completo per prima review sui gruppi (**_social_**) (sia su gruppo manifesti che su gruppo corso)
			- [ ] Aggiornare pagina sul sito con aule (**_social_**)
		- ({day_tamtam}) compilare PoliTamTam (**_direttivo_**)
			- [ ] done
		- ({three_weeks_bef}) Mandare in approvazione manifesto (**_direttivo_**)
			- [ ] Deadline manifesto completo con footer (**_social_**)
		- ({two_weeks_bef}) Stampare manifesti e appenderli (**_social_**)
			- [ ] 3 A3 (di cui uno in bacheca e 2 per l'aula)
			- [ ] 2 A4 Cartonato/plastificato (di cui uno da appendere in sede e uno da tenere per banchetti)
		- ({week_before}) Posts IG+TG w/ manifesto del corso (**_social_**)
			- [ ] Manifesto, orari, aule, descrizione, link al sito (**_social_**)
			- [ ] Deadline design storie instagram (**_social_**)
			- [ ] Deadline design thumbnail youtube (**_social_**)
			- [ ] Creare live (**_social_**) (verificare comportamento feed su live unlisted)
			- [ ] Schedule Posts telegram (12:00 del giorno del corso) (**_social_**)
		- ({day_before}) Pubblicare storia IG (**_social_**)
			- [ ] "ci vediamo domani"
		"""
	for day in days:
		text += f"""- ({day}) Pubblicare storia IG (**_social_**)
			- [ ] 12:00 (_storia IG_) promemoria corso
			- [ ] 12:00 (_messaggio TG_): luogo, ora, titolo lezione, timer, link alla stream"""

	return text

def create_links(course_name, short_name, dates):
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

