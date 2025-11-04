from __future__ import generators
import re
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))
from scraper import scrape_pad, get_pad_title
from datetime import timedelta
from jinja2 import Environment, FileSystemLoader

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
		for username in recipients.get(recipient, []):
			tags += f"{escape_markdown(username)}"
		if tags == "":
			tags = f"{escape_markdown(recipient)}"

		text = text.replace("**_" + recipient + "_**", tags)
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

	text = template_render("corso",
        {
			"course_name": course_name,
			"site_name": site_name,
        	"month_and_half_bef": month_and_half_bef.strftime("%Y-%m-%d"),
        	"month_before": month_before.strftime("%Y-%m-%d"),
        	"day_tamtam": day_tamtam.strftime("%Y-%m-%d"),
        	"three_weeks_bef": three_weeks_bef.strftime("%Y-%m-%d"),
        	"two_weeks_bef": two_weeks_bef.strftime("%Y-%m-%d"),
        	"week_before":  week_before.strftime("%Y-%m-%d"),
        	"day_before": day_before.strftime("%Y-%m-%d"),
			"days": days,
			"servizionlineurl": "https://servizionline.polimi.it/portaleservizi/portaleservizi/controller/preferiti/Preferiti.do?evn_srv=evento&idServizio="
		}
    )

	return text

def create_links(course_name: str, short_name: str, dates: list) -> str:
	"""Creates links for the course.
	args: course_name: name of the course
	short_name: short name of the course used in the website url
	dates: list of dates
	returns: links for the course
	"""
	year = dates[0].year
	links = template_render("links", {
			"year": year,
			"course_name": course_name,
			"short_name": short_name
		})
	return links

def template_render(file: str, options: dict) -> str:
	"""Render and returns template from /templates folder.
	file: template file
	*args: args passed to template (jinja documentation)
	returns: template compiled
	"""
	environment = Environment(loader=FileSystemLoader("templates/"))
	template = environment.get_template(file)

	text = template.render(options)

	return text
