#!/usr/bin/python
# -*- coding:utf-8 -*-
import datetime as dt
import logging
import os
import random
import sys
import time

from datetime import datetime, date
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from epd import epd4in2

from logger import logger

load_dotenv()
photos_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.getenv("PHOTO_DIR"))
fonts_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')

epd = epd4in2.EPD()
font64 = ImageFont.truetype(os.path.join(fonts_dir, 'font.ttc'), 64)
font24 = ImageFont.truetype(os.path.join(fonts_dir, 'font.ttc'), 24)

logging = logger.create_logger(__file__)


def main():
	epd.init()

	photo = str(sys.argv[1:][0]) if len(sys.argv[1:]) == 1 else None

	if photo:
		logging.info("Input Photo: {}".format(photo))

		if os.path.isfile(os.path.join(photos_dir, photo)):
			show_photo(photo, float(os.getenv("PHOTO_ONEOFF_DISPLAY_TIME_SEC")))
		else:
			logging.error("Photo not found: {}".format(photo))

		epd.Clear()
	else:
		show_banner()

		show_slideshow()


def calc_sleep_time():
	sleep_start_hh_mm = os.getenv("SLEEP_START_HH_MM")
	sleep_end_hh_mm = os.getenv("SLEEP_END_HH_MM")

	sleep_start_hh = int(sleep_start_hh_mm.split(":")[0])
	sleep_start_mm = int(sleep_start_hh_mm.split(":")[1])
	sleep_end_hh = int(sleep_end_hh_mm.split(":")[0])
	sleep_end_mm = int(sleep_end_hh_mm.split(":")[1])

	sleep_start_time = dt.time(sleep_start_hh, sleep_start_mm)
	sleep_end_time = dt.time(sleep_end_hh, sleep_end_mm)
	midnight_time = dt.time(0, 0)
	current_time = dt.datetime.now().time()

	if sleep_start_time < sleep_end_time:
		sleep_for_sec = (sleep_end_time.hour * 3600 + sleep_end_time.minute * 60 + sleep_end_time.second) - (current_time.hour * 3600 + current_time.minute * 60 + current_time.second)
		is_sleep = sleep_start_time < current_time < sleep_end_time
	else:
		if midnight_time <= current_time <= sleep_end_time:
			sleep_for_sec = (sleep_end_time.hour * 3600 + sleep_end_time.minute * 60 + sleep_end_time.second) - (current_time.hour * 3600 + current_time.minute * 60 + current_time.second)
			is_sleep = True
		elif sleep_start_time <= current_time:
			sleep_for_sec = 86400 - ((current_time.hour * 3600 + current_time.minute * 60 + current_time.second) - (sleep_end_time.hour * 3600 + sleep_end_time.minute * 60 + sleep_end_time.second))
			is_sleep = True
		else:
			sleep_for_sec = 0
			is_sleep = False

	logging.info("Sleeping: " + str(is_sleep))

	return is_sleep, sleep_for_sec


def show_banner():
	logging.info("Showing Banner")

	epd.Init_4Gray()
	epd.Clear()

	img = Image.new('L', (epd.width, epd.height), 0)  # 255: clear the frame
	draw = ImageDraw.Draw(img)
	draw.text((53, 80), 'Memories', font=font64, fill=epd.GRAY1)
	draw.line((10, 160, 390, 160), fill=epd.GRAY2)
	draw.text((135, 180), 'By Ujjal Dey', font=font24, fill=epd.GRAY3)
	epd.display_4Gray(epd.getbuffer_4Gray(img))
	time.sleep(float(os.getenv("BANNER_DISPLAY_TIME_SEC")))
	epd.Clear()


def show_photo(photo, sleep_time):
	try:
		logging.info("Reading bitmap photo: " + str(photo))
		Himage = Image.open(os.path.join(photos_dir, photo))
		epd.display(epd.getbuffer(Himage))
		time.sleep(sleep_time)
	except Exception as e:
		logging.error("error: " + str(e))


def show_slideshow():
	last_photo = ""

	try:
		while True:
			if os.getenv("SLEEP_ENABLED") == "True":
				is_sleep_time, sleep_time_sec = calc_sleep_time()

				if is_sleep_time and sleep_time_sec > 0:
					show_standby(sleep_time_sec)
					show_banner()

			photo = random.choice([p for p in os.listdir(photos_dir) if os.path.isfile(os.path.join(photos_dir, p))])
		
			if photo == last_photo:
				logging.info("Skipping")
			else:
				show_photo(photo, float(os.getenv("PHOTO_SLIDESHOW_DISPLAY_TIME_SEC"))) 
				pass

			last_photo = photo
	except IOError as e:
		logging.error("error: " + str(e))


def show_standby(sleep_time_sec):
	logging.info("Showing Standby for " + str(sleep_time_sec))

	epd.Init_4Gray()

	img = Image.new('L', (epd.width, epd.height), 0)  # 255: clear the frame
	draw = ImageDraw.Draw(img)
	draw.text((36, 80), 'Good Night', font=font64, fill=epd.GRAY1)
	draw.line((10, 160, 390, 160), fill=epd.GRAY2)
	draw.text((96, 180), 'See you tomorrow', font=font24, fill=epd.GRAY3)
	epd.display_4Gray(epd.getbuffer_4Gray(img))
	time.sleep(sleep_time_sec)
	epd.Clear()


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		logging.info("Ctrl-C pressed")
		epd4in2.epdconfig.module_exit()
		epd.Clear()
		epd.sleep()
		time.sleep(1)
		epd.Dev_exit()
		exit()
