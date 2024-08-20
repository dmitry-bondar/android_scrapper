import uiautomator2 as u2
import time
import re
import sys
import hashlib
from datetime import datetime
import modules.profiles as profiles
import modules.chunks as chunk
import modules.product as product
import modules.logger as log

d = u2.connect('192.168.56.102:5555')  # connect to device
print(d.info)

regionId = sys.argv[1]
taskId = sys.argv[2]
domain = "magnit.app"
sessionVar = str(
    domain + "_" + regionId + "_" + taskId + "_" + str(time.time())
).encode()

sessionHash = hashlib.new("sha1")
sessionHash.update(sessionVar)

sId = sessionHash.hexdigest()[-10:-1]

fileName = domain + "_" + regionId + "_" + taskId + "-" + sId
sessionDate = str(datetime.now().strftime("%Y-%m-%dT%H:%M:%S")) + "+0300"
logger = log.logger(fileName)

Product = product.Product(logger)

profile = profiles.get(taskId)
logger.log(profile)
sessionId = profile["sessions"][0]["id"]

progress = 0
chunkIds = []
chunkUrl = None
article = None
categoryId = 'Алкоголь'
storeName = profile["storeNames"][0]


def store():
    while not storeName:
        print(storeName)
        time.sleep(1)
    if d.xpath("//android.widget.TextView[@bounds='[121,95][963,153]']").click_exists(timeout=0.1):
        print('Click address')
        time.sleep(1)
    if d.xpath('//android.widget.TextView[@text="Адрес или название магазина"]').click_exists(timeout=0.1):
        d.send_keys(storeName)
        time.sleep(3)
    if d.xpath("//android.view.View[@bounds='[53,421][1027,590]']").click_exists(timeout=0.1):
        time.sleep(2)
    if d.xpath('//android.widget.TextView[@text="Перейти в каталог"]').click_exists(timeout=0.1):
        print("Выбрали магазин")
        time.sleep(2)


def openApp():
    if d.xpath('//android.widget.TextView[@text="Магнит"]').click_exists(timeout=0.1):
        print("Magnit  button click")
    time.sleep(6)
    if d.xpath('//android.widget.TextView[@text="В магазине"]').click_exists(timeout=0.1):
        print("Catalog button click")
    time.sleep(2)


def findCategory(categoryId):
    xPathCategory = '//android.widget.TextView[@text="{0}"]'.format(categoryId)
    while True:
        d.swipe(0, 800, 0, 0, 0.5)
        if d.xpath(xPathCategory).exists:
            d.xpath(xPathCategory).click_exists(timeout=0.1)
            print("Зашли в категорию {0}".format(categoryId))
            time.sleep(2)
            return True


def scrapeCategory():
    swipeCount = 1
    all_products = []
    swipe = 0
    for textBlock in d.xpath('//android.widget.ScrollView//android.widget.TextView').all():
        if re.search("товар", textBlock.text):
            textContProducts = textBlock.text
            countProducts = int(re.sub('\D+', '', textContProducts))
            swipeCount = int(countProducts / 4)

    d.swipe(0, 800, 0, 0, 0.5)
    while True:
        swipe += 1
        if d.xpath('//android.widget.TextView').exists:
            for elem in range(1, 5):
                new_products = []
                pathBlock = '//android.view.View/android.view.View[{0}]/android.widget.TextView'.format(elem)
                for textBlock in d.xpath(pathBlock).all():
                    regex = re.search("Искать|Алкоголь|товаров|По карте|магазине|Главная|Доставка|Журнал|-.*",
                                      textBlock.text)
                    if not regex and not textBlock.attrib.get("resource-id") == 'com.android.systemui:id/clock':
                        new_products.append(re.sub('₽', '', textBlock.text, 0, re.MULTILINE))
                print(new_products)
                if len(new_products) == 4:
                    countRewievs = new_products[3].split(' · ')
                    all_products.append({
                        "price": re.sub(',', '.', new_products[0], 0, re.MULTILINE),
                        "old_price": re.sub(',', '.', new_products[1], 0, re.MULTILINE),
                        "name": new_products[2],
                        "rating": countRewievs[0],
                        "countRewievs": countRewievs[1] if len(countRewievs) > 1 else ''
                    })
                elif len(new_products) == 3:
                    countRewievs = new_products[2].split(' · ')
                    all_products.append({
                        "price": re.sub(',', '.', new_products[0], 0, re.MULTILINE),
                        "name": new_products[1],
                        "rating": countRewievs[0],
                        "countRewievs": countRewievs[1] if len(countRewievs) > 1 else ''
                    })
        if swipeCount <= swipe:
            print(all_products)
            return True
        d.swipe(0, 1870, 0, 0, 0.5)


def main():
    openApp()
    store()
    findCategory(categoryId)
    scrapeCategory()


if __name__ == "__main__":
    main()
