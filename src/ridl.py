import requests
import validators
from colorama import init, Fore, Style

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

		time.sleep(1) # Wait 1 second to prevent unnecessary CPU usage
