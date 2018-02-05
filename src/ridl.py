import json
import os
import requests
import validators
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
from PIL import Image

image_folder = 'images/'
image_folder_backup = image_folder + 'backup/'

headers = {}
headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'

google_url     = 'https://www.google.com'
google_ris_url = 'https://www.google.com/searchbyimage?&image_url=' # ris = Reverse Image Search

def is_image_url(url):
	# First check whether the provided string is a URL at all
	if not validators.url(url):
		print('Not a URL')
		return False

	# Check the content-type of the object at the URL to determine whether it's an image
	try:
		response = requests.head(url)
		response.raise_for_status()

	except requests.exceptions.HTTPError        as e: print(Fore.RED + 'HTTP Error: '        + str(e))
	except requests.exceptions.ConnectionError  as e: print(Fore.RED + 'Connection Error: '  + str(e))
	except requests.exceptions.Timeout          as e: print(Fore.RED + 'Timeout: '           + str(e))
	except requests.exceptions.RequestException as e: print(Fore.RED + 'Request Exception: ' + str(e))

	else:
		response = requests.head(url)
		mimetype = response.headers.get('content-type')

		if mimetype.split('/')[0] == 'image':
			return True

	print('Not an image URL')
	return False

def download_image(url, path):
	# Get the local target path
	filename = url.split('/')[-1]
	target = path + filename

	# Create the folders in the target path if they don't already exist
	if not os.path.exists(os.path.dirname(target)):
		os.makedirs(os.path.dirname(target))

	# Some image URLs have extra text after the filename, or don't display the file extension. Deal with these cases
	response = requests.head(url)
	mimetype = response.headers.get('content-type')

	if '.' not in target:
		target += '.' + mimetype.split('/')[-1] # Add the appropriate extension to the target filename

	elif len(target.split('.')[-1]) > 4: # Handles the case of a URL like "2b.jpg&..."
		target = '.'.join(target.split('.')[:-1]) + '.' + mimetype.split('/')[-1]

	# Add a number to the target filename if it already exists (starting at 2, same as Windows)
	target_final = target

	n = 1
	while os.path.isfile(target_final):
		n += 1
		target_final = '.'.join(target.split('.')[:-1]) + ' (' + str(n) + ').' + target.split('.')[1]

	# Download the image and save it to file
	print(Fore.CYAN + target_final + Fore.WHITE + ' < ' + Fore.BLUE + url + Fore.WHITE + ' ... ', end = '')

	image = requests.get(url, stream=True)
	with open(target_final, 'wb') as f:
		for chunk in image.iter_content(chunk_size=1024):
			if chunk: # Filter out keep-alive chunks
				f.write(chunk)

	print(Fore.GREEN + 'Saved' + Style.RESET_ALL + Style.BRIGHT)

	# Return the saved filename, since the image needs to be accessed later to find its size
	return target_final.split('/')[-1]

def get_page_soup(url):
	"""Returns the page at the URL as a parsable BeautifulSoup object."""

	response = requests.get(url, headers=headers)
	print(Fore.BLACK + 'Got response: ' + str(response.status_code))

	if response.status_code < 200 or response.status_code >= 300:
		return False

	return BeautifulSoup(response.text, 'lxml')

def download_best_image(url, original_image_filename):
	"""
	Uses Google's reverse image search to try and find a larger version of the image at the supplied URL.
	
	:returns: True if a valid image was found, False otherwise
	"""

	# Get the size of the original image, since we need to find only a larger one
	original_image_path = image_folder_backup + original_image_filename
	original_image = Image.open(original_image_path)

	oiw, oih = original_image.size
	original_image_size = oiw + oih # A simple but effective way of representing the image's size

	print(Fore.WHITE + 'Original image: ' + Fore.MAGENTA + str(oiw) + 'x' + str(oih))

	# Do the reverse image search
	print(Fore.BLACK + 'Searching Google for matching images... ', end='')

	results_page = get_page_soup(google_ris_url + url)
	if not results_page:
		print(Fore.RED + 'Failed to query Google')
		return False

	other_sizes_div = results_page.find('div', id='_w6')
	if not other_sizes_div:
		# This div still exists even if no similar images were found, so the parsing itself must have failed
		print(Fore.RED + 'Failed to parse results page')
		return False

	other_sizes_links = other_sizes_div.find_all('a')
	if not len(other_sizes_links):
		print(Fore.YELLOW + "Google couldn't find any matching images")
		return False

	largest_found_size_url = other_sizes_links[-1].get('href') # Will link to the Large, Medium, or Small images page
	print(Fore.BLACK + 'Checking ' + other_sizes_links[-1].string + ' images... ', end='')

	images_page = get_page_soup(google_url + largest_found_size_url)
	if not images_page:
		print(Fore.RED + 'Failed to query Google')
		return False
	
	# Form a list of the found images. We will get all the data Google provides for each image
	images = images_page.find_all(class_='rg_meta')
	if not images:
		print(Fore.RED + 'Failed to parse images page')
		return False

	for image in images:
		# We can convert the image data to JSON, which will contain the image's width, height, and true URL
		image_json = json.loads(image.string)

		width     = image_json['ow']
		height    = image_json['oh']
		image_url = image_json['ou']

		if width + height > original_image_size:
			# Ensure that the image can be accessed, as the host could be down, or the file removed/inaccessible
			if not is_image_url(image_url):
				print(Fore.BLACK + 'Failed to access image URL; trying next one...')
				continue

			print(Fore.GREEN + 'Successfully found larger image: ' + Fore.MAGENTA + str(width) + 'x' + str(height))
			download_image(image_url, image_folder)

			return True

		else:
			print(Fore.YELLOW + "Google couldn't find any larger images")
			return False

if __name__ == '__main__':
	import argparse
	import pyperclip
	import time

	# Check command-line arguments
	parser = argparse.ArgumentParser()
	
	parser.add_argument('-s', '--single_folder', action='store_true',
		help="If a larger image isn't found, move the original image to the main image folder.")

	args = parser.parse_args()

	init() # Colorama
	print(Style.BRIGHT) # Make all printed text bright (Fore.BLACK becomes grey, colours aren't dim)

	last_clip = ''

	# Continuously check for changes to the clipboard
	while True:
		clip = pyperclip.paste()

		if clip != last_clip: # Something was copied to the clipboard
			last_clip = clip

			print(Fore.BLACK + 'Checking... ', end='')
			if is_image_url(clip):
				print(Fore.GREEN + 'Image detected!')

				# First download the image to the backup folder, then try to find a larger image to save
				original_image_filename = download_image(clip, image_folder_backup)
				found_image = download_best_image(clip, original_image_filename)

				# If the "single folder" option is enabled and a larger image wasn't found, move the original image to the main folder
				if args.single_folder and not found_image:
					src = image_folder_backup + original_image_filename
					dest = image_folder + original_image_filename

					os.rename(src, dest)
					print(Fore.BLACK + 'Moved ' + src + ' to ' + dest)

				# For clarity, leave a blank line after each reverse image download
				print('')

		time.sleep(1) # Wait 1 second to prevent unnecessary CPU usage
