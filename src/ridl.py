import os
import requests
import validators
from colorama import init, Fore, Style

image_folder = 'images/'
image_folder_backup = image_folder + 'backup/'

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

if __name__ == '__main__':
	import pyperclip
	import time

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
				download_image(clip, image_folder_backup)

				# For clarity between individual images, leave a blank line
				print('')

		time.sleep(1) # Wait 1 second to prevent unnecessary CPU usage
