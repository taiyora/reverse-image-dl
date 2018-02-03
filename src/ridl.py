if __name__ == '__main__':
	import pyperclip
	import time

	last_clip = ''

	# Continuously check for changes to the clipboard
	while True:
		clip = pyperclip.paste()

		if clip != last_clip: # Something was copied to the clipboard
			last_clip = clip
			print(clip)

		time.sleep(1) # Wait 1 second
