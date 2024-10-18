from __future__ import generators
import re
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))
from scraper import scrape_pads

def match_next_date(text):
    """(yyyy-mm-dd)"""
    return re.search(r"(\d{4})-(\d{2})-(\d{2})", text)


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
						text += "\n" + task.replace("- [ ]", "\u2757")
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



