import logging
from datetime import datetime
import sys

terminalLog = False
if "--log" in sys.argv:
    terminalLog = True

class logger():
    def __init__(self, fileName):
        pass
        logging.basicConfig(filename="/opt/android_scraper/sessions/" + fileName + ".log", encoding='utf-8', level=logging.INFO)

    def log(self, string):
        string = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + "   " + str(string)
        logging.info(string)
        if terminalLog == True:
            print(string)