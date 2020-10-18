import wave
import sys
import base64
import snowboydecoder
from pymongo import MongoClient
import urllib.parse

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


identDoc = identificationRequests.find_one({
    "status": 0
})
hotWord = activationWords.find_one({
    "_id": identDoc._id
})

models = "model.pmdl"
fromBase64ToFile(getBase64FromID(hotWord.trainingModel), models)

recording = "recording.wav"
fromBase64ToFile(getBase64FromID(identDoc.idRecording), recording)
f = wave.open(recording)
assert f.getnchannels(
) == 1, "Error: Snowboy only supports 1 channel of audio (mono, not stereo)"
assert f.getframerate() == 16000, "Error: Snowboy only supports 16K sampling rate"
assert f.getsampwidth() == 2, "Error: Snowboy only supports 16bit per sample"
data = f.readframes(f.getnframes())
f.close()


sensitivity = 0.5
detection = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity)

ans = detection.detector.RunDetection(data)

if (ans == 1):
    identificationRequests.update_one({
        "_id": identDoc._id
    }, {
        "$set": {
            "status": 1
        }
    })
else:
    identificationRequests.update_one({
        "_id": identDoc._id
    }, {
        "$set": {
            "status": 0
        }
    })
