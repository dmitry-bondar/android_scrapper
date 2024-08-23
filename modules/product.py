import re
import json
import requests as req
import json
from datetime import datetime

queue = []
queueLength = 200


class Product:
    def __init__(self, logger):
        self.logger = logger

    def create(self, productParams, sessionDate):
        try:
            if len(productParams["onlinePrice"]) > 0:
                price = productParams["onlinePrice"]
                price = re.sub(r",", ".", price)
                price = re.sub(r"[^\d+\.]", "", price)
                productParams["price"] = {"value": "", "currency": ""}
                productParams["price"]["value"] = float(price)
                productParams["price"]["currency"] = (
                    productParams["currency"]
                    if productParams.get("currency")
                    else "RUR"
                )
            del productParams["onlinePrice"]

            if "discountPrice" in productParams and len(productParams["discountPrice"]) > 0:
                discountPrice = productParams["discountPrice"]
                discountPrice = re.sub(r",", ".", discountPrice)
                discountPrice = re.sub(r"[^\d+\.]", "", discountPrice)
                if discountPrice:
                    productParams["discountPrice"] = float(discountPrice)

            if "specPrice" in productParams and len(productParams["specPrice"]) > 0:
                specPrice = productParams["specPrice"]
                specPrice = re.sub(r",", ".", specPrice)
                specPrice = re.sub(r"[^\d+\.]", "", specPrice)
                if specPrice:
                    productParams["specPrice"] = str(float(specPrice))

            productParams["categories"] = list(
                filter(lambda el: not (re.match(r"Главная|Каталог", el)), productParams["categories"]))
            productParams["template"] = {
                "collected": str(datetime.now().strftime("%Y-%m-%dT%H:%M:%S")) + '+0300',
                "sessionLocalDate": str(datetime.now().strftime("%Y-%m-%dT%H:%M:%S")) + '+0300',
                "sessionId": productParams["sessionId"],
                "templateUri": "templates." + productParams["marketId"] + ":template",
                "collectMethod": "scripting",
                "sessionDate": sessionDate
            }
            queue.append(productParams)
        except Exception as ex:
            self.logger.log("Product create error: " + str(ex))
        finally:
            self.logger.log(json.dumps(productParams, ensure_ascii=False))
        if len(queue) >= queueLength:
            self.sendToSystem()

    def sendToSystem(self, toSend=False, tryIndex=0):
        tryIndex += 1
        toSend = toSend or queue[0:queueLength]
        del queue[0:queueLength]
        self.logger.log("Попытка отправки # " + str(tryIndex))
        self.logger.log("Продуктов в очереди: " + str(len(queue)))
        self.logger.log("send to system: " + str(len(toSend)))
        try:
            data = json.dumps({
                "messages": toSend
            }, ensure_ascii=False).encode('utf-8')
            r = req.post(
                "http://api.metacommerce.io/internal/products/queue?apiKey=9049719c-eea3-45ed-9371-34af34618ea9", data)
            if r.status_code == 400:
                self.logger.log("============")
                self.logger.log("Bad products")
                self.logger.log(json.dumps(r.json(), ensure_ascii=False))
                self.logger.log("============")
            elif r.status_code == 200:
                self.logger.log("============")
                self.logger.log("Products completed: " + json.dumps(r.json(), ensure_ascii=False))
                self.logger.log("============")
            else:
                self.logger.log("============")
                self.logger.log("Something wrong with products API. Retrying...")
                self.logger.log("============")
                self.sendToSystem(toSend=toSend, tryIndex=tryIndex)
        except Exception as ex:
            self.logger.log("Error: " + str(ex))
        return
