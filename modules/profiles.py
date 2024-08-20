import requests as req
import time

def get(taskId):
    r = req.get('http://api.metacommerce.io/internal/extraction/online/task/profiles?apiKey=9049719c-eea3-45ed-9371-34af34618ea9')
    if r.status_code == 200:
        # print(r.status_code)
        response = r.json()
        for dict in response:
            if taskId in dict['profileId']:
                return dict
    else:
        time.sleep(15)
        return get(taskId)