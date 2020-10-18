import sys
import base64
import requests
import snowboydecoder
from pymongo import MongoClient


def fromBase64ToFile(base64Data, fileDest):
	chunk = base64.b64decode(base64Data)
	with open(fileDest, 'wb') as f:
		f.write(chunk)


conn = MongoClient(
    "mongodb:root@password//localhost:27017/?auth=keyvox-test")

keyvox = conn["keyvox-test"]

identificationRequests = keyvox["identificationRequests"]
activationWords = keyvox["activationWords"]


endpoint = "https://snowboy.kitt.ai/api/v1/train/"
token = "956f276855b6922217e762600143eadc4c1b3797"
hotword_name = ""
language = "es"

identDoc = identificationRequests.find_one({
	status: 0
})
activationWords.find_one({
	_id: identDoc._id
})

data = {
    "name": hotword_name,
    "language": language,
    "token": token,
    "voice_samples": [
        {"wave": get_wave(wav1)},
        {"wave": get_wave(wav2)},
        {"wave": get_wave(wav3)}
    ]
}
response = requests.post(endpoint, json=data)
   if response.ok:
        with open(out, "w") as outfile:
            outfile.write(response.content)
        print "Saved model to '%s'." % out
    else:
        print "Request failed."
        print response.text

endpoint = "https://snowboy.kitt.ai/api/v1/train/"
