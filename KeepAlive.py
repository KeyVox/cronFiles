# -*- coding: utf-8 -*-
import yaml
import datetime
import time
import pymysql
import random
import urllib
from pymongo import MongoClient

path:str = "/etc/keyvox/keepalive.yml"
pathAsterisk:str = ""
mongoURL:str = ""
dbName:str = ""
voz:str = ""
inicioJIVR:int = 0
finJIVR:int = 0
conexionMysql = {
    "host":"",
    "user":"",
    "password":"",
    "port":0,
    "dbName":""
}
with open(path,'r') as file:
    configuracion = yaml.load(file, Loader=yaml.FullLoader)
    mongoURL = "mongodb://"+configuracion["mongo"]["user"]+":"+urllib.parse.quote(configuracion["mongo"]["password"])+"@"+configuracion["mongo"]["host"]+":"+str(configuracion["mongo"]["port"])+"/?authSource="+configuracion["mongo"]["database"]
    dbName = configuracion["mongo"]["database"]
    conexionMysql["host"] = configuracion["mysql"]["host"]
    conexionMysql["user"] = configuracion["mysql"]["user"]
    conexionMysql["password"] = configuracion["mysql"]["password"]
    conexionMysql["port"] = configuracion["mysql"]["port"]
    conexionMysql["dbName"] = configuracion["mysql"]["database"]
    voz = configuracion["idVoz"]
    inicioJIVR = configuracion["JIVR"]["inicio"]
    finJIVR = configuracion["JIVR"]["fin"]
    pathAsterisk = configuracion["pathAsterisk"]
client = MongoClient(mongoURL)
db = client[dbName]

while True:
    print("Iniciando ciclo")
    for x in db.calls.find({"status":0}):
        conexionMysql = pymysql.connect(host=conexionMysql.host, user=conexionMysql.user, passwd=conexionMysql.password, database=conexionMysql.dbName,port=conexionMysql.port)
        cursor = conexionMysql.cursor()
        fecha = datetime.datetime.utcnow()
        print("Hay una llamada pendiente de marcar con id %s", str(x._id))        
        palabraActivacion = db.activationWords.find_one({"_id":x.idActivationWord})
        print("La palabra de activacion es: %d",palabraActivacion.name)
        cliente = db.accounts.find_one({"_id":x.idAccount})
        print("El cliente es: %d",cliente.name)
        solicitudIdentificacion = db.identificationRequests.find_one({"_id":x.idIdentificationRequest})
        print("La solicitud de identificacion tiene el id %d",solicitudIdentificacion._id)
        tts:str = "Hola "+cliente.name+", por favor di tu palabra de activacion: "+palabraActivacion.name+" para confirmar tu compra en "+solicitudIdentificacion.source
        print("El TTS es: "+tts)
        cpuname:int = random.randint(inicioJIVR, finJIVR)
        aleatorio:int = random.randint(100,999)
        idTTS:int = 1
        cursor.execute("SELECT id FROM tbl_audio ORDER BY id DESC LIMIT 1")
        anteriores = cursor.fetchall()
        for anterior in anteriores:
            idTTS = int(anterior["id"])+1
        cursor.execute("INSERT INTO tbl_audio (id,aleatorio,voz,mensaje,generado,cpuname) VALUES ("+str(idTTS)+","+str(aleatorio)+",'"+tts+"',0,"+str(cpuname)+")")
        conexion.commit()
        salir:bool = False
        while not salir:        
            time.sleep(1)    
            cursor.execute("SELECT generado FROM tbl_audio WHERE id = "+idTTS)            
            for resultado in cursor.fetchall() and not salir:
                if resultado["generado"] == 1:
                    salir = True            
        conexion.close()
        idTTS_str:str = str(aleatorio)+str(idTTS)
        while(len(idTTS_str)<6):
            idTTS_str = "0"+idTTS_str
        contenidoArchivo:str = "Channel: SIP/DIRECTO/896852"+cliente.phoneNumber+"\nMaxRetries: 2\nCallerid: \"5570991200\"\nRetryTime: 2000\nWaitTime: 30\nArchive: yes\nContext: default\nExtension: 851"+idTTS_str+str(x._id)+"\nPriority: 1"
        print("El archivo tiene: %s"+contenidoArchivo)
        with open(pathAsterisk+str(x._id), 'w') as archivoDestino:
            archivoDestino.write(contenidoArchivo)
        print("Escribi el archivo en: "+pathAsterisk+"/"+str(x._id))
        db.calls.update_one({"_id":x._id},{"$set":{"status":1,"dateInitiated":fecha}})
        print("Actualize la llamada")                
    print("Termine ciclo")    
