# reverse-image-dl (RIDL)
RIDL (pronounced "riddle") is a small script that monitors the clipboard and, upon detecting an image URL, uses Google's reverse image search capabilities to find the largest possible version of that image.

![RIDL](https://github.com/taiyora/reverse-image-dl/blob/master/screenshots/2018-02-05%20Light.png)

Planned features include:
 * Ability to detect and upload image files in addition to URLs.
 * Support for other reverse image search services.
 * A gallery and management interface, including features like bulk image replacement.

### Usage
RIDL will save any image you copy in addition to the larger version it finds (if any). This is because larger images are not always better quality. Reverse image search services also occasionally return images that are slightly different to the original: cropping, watermarks, and off-tone colours can be found. The original image is saved so that a manual check and replacement can be done later.

By default, original images are saved to `images/backup/` while found images are placed in `images/`.

## Install
Python 3 is required.

`pip install -r requirements.txt`

## Run
`python ridl.py`

The following command-line arguments are available:

 * `-s` `--single_folder` If a larger image isn't found, move the original image to the main image folder.

   This is useful when using RIDL as an image downloader, as the main folder will hold your full image collection, rather than just those found via reverse image search.
