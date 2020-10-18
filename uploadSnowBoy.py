import sys
import base64
import requests
import snowboydecoder
from pymongo import MongoClient


conn = MongoClient(
    "mongodb://"+urllib.parse.quote_plus("keyvox-webapp")+"@"+urllib.parse.quote_plus("7Kb443PWqFBP5iO84pnSYA==") + "@104.238.138.234:27017/?authSource=keyvox-test")

keyvox = conn["keyvox-test"]

identificationRequests = keyvox["identificationRequests"]
activationWords = keyvox["activationWords"]
files = keyvox["files"]


def fromBase64ToFile(base64Data, fileDest):
    chunk = base64.b64decode(base64Data)
    with open(fileDest, 'wb') as f:
        f.write(chunk)


def getBase64FromID(ID):
    return files.find_one({
        "_id": ID
    }).value.data


def getBase64FromFile(fname):
    with open(fname) as infile:
        return base64.b64encode(infile.read())


endpoint = "https://snowboy.kitt.ai/api/v1/train/"
token = "956f276855b6922217e762600143eadc4c1b3797"
language = "es"

hotWord = activationWords.find_one({
    "status": 0
})
hotword_name = hotWord.name
waves = []
for sample in hotWord.samples:
    waves.append(getBase64FromID(sample))

data = {
    "name": hotword_name,
    "language": "es",
    "token": token,
    "voice_samples": [
        {"wave": waves[0]},
        {"wave": waves[1]},
        {"wave": waves[2]}
    ]
}
response = requests.post(endpoint, json=data)
out = "newModel.pmdl"
if response.ok:
    with open(out, "w") as outfile:
        outfile.write(response.content)

        newFile = files.insert_one({
            "name": "",
            "desc": "",
            "value": {
                    "data": getBase64FromFile(out),
                "contentType": "application/octet-stream",
                "ext": "pmdl"
            }
        })
    activationWords.update_one({"_id": hotWord._id}, {
        "$set": {
            "status": "1",
            "trainingModel": newFile._id
        }
    })


else:
    activationWords.update_one({"_id": hotWord._id}, {
        "$set": {
            "status": "2"
        }
    })
