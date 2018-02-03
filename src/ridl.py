import requests
import validators

def is_image_url(url):
	# First check whether the provided string is a URL at all
	if not validators.url(url):
		print('Not a URL')
		return False

	# Check the content-type of the object at the URL to determine whether it's an image
	try:
		response = requests.head(url)
		response.raise_for_status()

	except requests.exceptions.HTTPError        as e: print('HTTP Error: '        + str(e))
	except requests.exceptions.ConnectionError  as e: print('Connection Error: '  + str(e))
	except requests.exceptions.Timeout          as e: print('Timeout: '           + str(e))
	except requests.exceptions.RequestException as e: print('Request Exception: ' + str(e))

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

	last_clip = ''

	# Continuously check for changes to the clipboard
	while True:
		clip = pyperclip.paste()

		if clip != last_clip: # Something was copied to the clipboard
			last_clip = clip

			print('Checking... ', end='')
			if is_image_url(clip):
				print('Image detected!')

		time.sleep(1) # Wait 1 second
