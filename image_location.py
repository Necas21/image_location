import requests
import os
import sys
from bs4 import BeautifulSoup
from PIL import Image, ExifTags
import argparse
import shutil


# Returns a list of img URLs from a website
def get_images(url):
	res = requests.get(url)
	html = res.text
	soup = BeautifulSoup(html, "html.parser")
	images = []

	for img in soup.find_all("img"):
		images.append(img.get("src"))

	return images


# Takes a list of image URLs and downloads them to the 'results' directory. Returns the path to the file.
def download_image(img_url):
	try:
		r = requests.get(img_url)

		if r.ok and len(r.content) > 0:
			print(f"[*] Downloading image from: {img_url}")
			img_name = img_url.split("/")[-1]
			path = f"results/{img_name}"
			f = open(path, "wb")
			f.write(r.content)
			f.close()
			print(f"[+] Saving {img_name}")

	except:
		print(f"[-] Download Failed")


# Takes an image name and returns the Exif data
def get_exif(img_file_name):
	try:
		exif_data = {}
		img = Image.open(img_file_name)
		info = img._getexif()

		if info:
			for (tag, value) in info.items():
				exif_data[ExifTags.TAGS.get(tag)] = value

			exif_gps = exif_data["GPSInfo"]
			img_file_name = img_file_name.split("/")[1]
			print(f"[*] Found GPS Info for: {img_file_name}")

			if exif_gps:
				for key in exif_gps:
					decoded_value = ExifTags.GPSTAGS.get(key)
					print(f"[+] {decoded_value}: {exif_gps[key]}")

	except:
		pass


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-u", dest="url", help="Specify a URL to scrape for images")

	if len(sys.argv) != 3:
		parser.print_help(sys.stderr)
		sys.exit(1)

	args = parser.parse_args()
	url = args.url

	try:
		os.mkdir("results")

	except:
		shutil.rmtree("results")
		os.mkdir("results")

	images = get_images(url)

	for image in images:
		download_image(image)

	image_files = os.listdir("results")

	for image in image_files:
		get_exif(f"results/{image}")


if __name__ == "__main__":
	main()
