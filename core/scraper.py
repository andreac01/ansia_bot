import requests
from bs4 import BeautifulSoup
import time
import os

# Function to scrape content from the given URL
def scrape_pad(url: str, relative_path='../data') -> None:
	"""Scrape the content of a CodiMD pad and save it to a file.
	args: url: URL of the CodiMD pad
	relative_path: relative path to save the content
	"""
	try:
		response = requests.get(url)
		# Check if request was successful
		if response.status_code == 200:
			# Parse the HTML content
			soup = BeautifulSoup(response.text, 'html.parser')
			# Find the title of the page
			title = str(soup.title.string.split(' - HedgeDoc')[0]).replace(' ', '_')
			# find markdown content
			markdown = soup.find_all('div', class_='container markdown-body')
			# Find the content (depending on the structure of the page)
			content = markdown[0].get_text()

			# Save the content to a file
			save_path = os.path.join(os.path.dirname(__file__), relative_path)
			if not os.path.exists(save_path):
				os.makedirs(save_path)
			with open(f'{save_path}/{title}.md', 'w') as f:
				f.write(content)
		else:
			print(f"Failed to retrieve page. Status code: {response.status_code}")

	except Exception as e:
		print(f"An error occurred during: {e}")

def get_pad_title(url: str) -> str:
	"""Get the title of a CodiMD pad.
	args: url: URL of the CodiMD pad
	returns: title of the pad
	"""
	response = requests.get(url)
	if response.status_code == 200:
		soup = BeautifulSoup(response.text, 'html.parser')
		title = str(soup.title.string.split(' - HedgeDoc')[0]).replace(' ', '_')
		return title
	return None
