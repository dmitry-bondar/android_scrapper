import modules.chrome as chrome
import modules.profiles as profiles
import modules.chunks as chunk
import modules.product as product
import modules.logger as log
import aptekiplus_regions as regions
from selenium.webdriver.common.by import By
import sys
import hashlib
import time
import re
from pyquery import PyQuery as pq
from datetime import datetime

# from xvfbwrapper import Xvfb
#
# vdisplay = Xvfb(width=1280, height=1024, colordepth=24)
# vdisplay.start()

import os

os.environ["DISPLAY"] = ":99"

regionId = sys.argv[1]
taskId = sys.argv[2]
domain = "holodilnik.ru"
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
browser = chrome.Chrome(logger)
# time.sleep(1200)
# time.sleep(600)

profile = profiles.get(taskId)
logger.log(profile)
sessionId = profile["sessions"][0]["id"]
# print(profile["sessions"][0]["id"])

progress = 0
chunkIds = []
chunkUrl = None
article = None


def card(content, url, chunk):
    jq = pq(content)
    categories = jq.find(".breadcrumb li a").map(lambda i, e: pq(e).text().strip())
    if jq.find('.empty_onStock').length:
        availability = 'OutOfStock'
    else:
        availability = 'InStock'

    productParams = {
        "name": jq.find('h1').text().strip(),
        "url": url,
        "categories": categories,
        "onlinePrice": re.sub(r'\D+', '', jq.find(".product-price__current").text().strip()),
        # "discountPrice": jq.find(".action-product__price-old.price__item--old").eq(0).text().strip(),
        "availability": availability,
        "imageUrls": ["https:" + jq.find(".card-product-img__inner img").attr("src")],
        "marketId": domain,
        "regionId": regionId,
        "source": "Origin",
        "sessionId": sId,
        "fetchUrl": url,
        "custom": {
            "onlineTaskId#0": profile["sessions"][0]["taskId"],
            "onlineTaskClientId#0": profile["sessions"][0]["clientId"],
            "onlineTaskSessionId#0": sessionId,
            "workspaceIds#0": chunk["workspaceIds"][0],
            "onlineTaskChunkUrl": chunk["url"] if chunk.get("url") else None,
            "onlineTaskChunkQuery": chunk["query"] if chunk.get("query") else None,
            "onlineTaskChunkQueryArticle": chunk["queryArticle"] if chunk.get("queryArticle") else None,
            "onlineTaskChunkArticle": chunk["article"] if chunk.get("article") else None,
            "onlineTaskChunkUrlArticle": chunk["urlArticle"] if chunk.get("urlArticle") else None,
        },
    }
    Product.create(productParams, sessionDate)


def processChunk(chunk):
    chunkUrl = chunk["url"]
    content = browser.goto(chunkUrl, selectors="footer")
    if content != False:
        jq = pq(content)
        if jq.find('[data-page-type="goodsList"]').length:
            category(content=content, url=chunkUrl, chunk=chunk)
        elif jq.find(".card-product-page").length:
            card(content=content, url=chunkUrl, chunk=chunk)


def category(content, url, chunk):
    def collectItem(index, content, categories):
        el = pq(content)
        onlinePrice = (
            el.find(".price .price__value").text().strip()
        )
        if onlinePrice is None:
            availability = 'OutOfStock'
        else:
            availability = 'InStock'

        productParams = {
            "name": el.find(".product-name a").text().strip(),
            "url": el.find(".product-name a").attr("href"),
            "categories": categories,
            "onlinePrice": onlinePrice,
            # "discountPrice": el.find(".amount__item--old").eq(0).text().strip(),
            "availability": availability,
            "imageUrls": ["https:" + el.find(".img-fluid").attr("src")],
            "marketId": domain,
            "regionId": regionId,
            "source": "Origin",
            "sessionId": sId,
            "fetchUrl": url,
            "custom": {
                "onlineTaskId#0": profile["sessions"][0]["taskId"],
                "onlineTaskClientId#0": profile["sessions"][0]["clientId"],
                "onlineTaskSessionId#0": sessionId,
                "workspaceIds#0": chunk["workspaceIds"][0],
                "onlineTaskChunkUrl": chunk["url"] if chunk.get("url") else None,
                "onlineTaskChunkQuery": chunk["query"] if chunk.get("query") else None,
                "onlineTaskChunkQueryArticle": chunk["queryArticle"] if chunk.get("queryArticle") else None,
                "onlineTaskChunkArticle": chunk["article"] if chunk.get("article") else None,
                "onlineTaskChunkUrlArticle": chunk["urlArticle"] if chunk.get("urlArticle") else None
            },
        }
        Product.create(productParams, sessionDate)

    def collect(content):
        jq = pq(content)
        categories = jq.find(".breadcrumb li span").map(
            lambda i, e: pq(e).text().strip()
        )
        if profile["followCards"] == True:
            links = jq.find(".goods-tile.preview-product").map(
                lambda i, e: pq(e).find(".product-name a").attr("href")
            )
            for link in links:
                cardContent = browser.goto(link, selectors="footer")
                card(content=cardContent, url=link, chunk=chunk)

        else:
            jq.find(".goods-tile.preview-product").each(
                lambda i, e: collectItem(index=i, content=e, categories=categories)
            )

    collect(content)
    jq = pq(content)
    if profile["pagerDepth"] < 0:
        pagerLimit = 999
    else:
        pagerLimit = profile["pagerDepth"]
    currentPage = 1
    while currentPage < pagerLimit:
        nextPage = jq.find(".pagination .page-next .page-link").attr("href")
        logger.log("nextpage : ")
        logger.log(nextPage)
        if (nextPage):
            if profile["mode"] == "search":
                nextPageUrl = ''
            else:
                nextPageUrl = nextPage
            content = browser.goto(nextPageUrl, selectors="footer")
            jq = pq(content)
            collect(content)
        else:
            currentPage = 99999


"""
def setRegion(url):
    region = regions.dict[regionId]
    url = re.sub(
        r"holodilnik.ru\/(.*?)\/product", "aptekiplus.ru/" + region + "/product", url
    )
    url = re.sub(
        r"aptekiplus.ru\/(.*?)\/catalog", "aptekiplus.ru/" + region + "/catalog", url
    )
    return url 
"""

while progress < 1:
    logger.log("progress: " + str(progress))
    chunks = []
    # logger.log(chunkIds)
    chunksData = chunk.get(sessionId, chunkIds=chunkIds)
    logger.log(chunksData)
    chunkIds = []
    progress = chunksData["stats"][sessionId]["progress"]
    for c in chunksData["chunks"]:
        if profile["mode"] != "articles":
            chunkIds.append(c["id"])
        if profile["mode"] == "search":
            chunks.append(
                {
                    "url": "https://aptekiplus.ru/moskva/catalog/root/?q=" + c["query"],
                    "workspaceIds": c["workspaceIds"],
                    # "article": c["article"]
                }
            )
        elif profile["mode"] == "links":
            # logger.log(c["url"])
            chunks.append(
                {
                    "url": c["url"],  # setRegion(c["url"]),
                    "workspaceIds": c["workspaceIds"],
                    # "article": c["article"]
                }
            )
    logger.log(chunks)
    for c in chunks:
        processChunk(chunk=c)
    time.sleep(10)

Product.sendToSystem()
browser.close()
logger.log("Session complete")
# vdisplay.stop()
