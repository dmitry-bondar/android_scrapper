import requests as req
import time
import json

def get(sessionId, chunkIds=[]):
    # print(sessionId)
    # print(chunkIds)
    data = json.dumps({
			"size": 10,
			"sessionIds": [sessionId],
			"completedChunkIds": chunkIds
		})
    # print("post chunk" + data)
    r = req.post('http://api.metacommerce.io/internal/extraction/online/task/chunks/next?apiKey=9049719c-eea3-45ed-9371-34af34618ea9', data)
    if r.status_code == 200:
        return r.json()
    else:
        time.sleep(30)
        return get(sessionId=sessionId, chunkIds=chunkIds)