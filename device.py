from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

import signal
import sys
import time
import json
import threading
from threading import Thread
import copy
from functools import partial

from NtpSyncTime import NtpSyncTime
from measurements.net import NetMeasurement
from measurements.cpuMemoryLoad import CpuMemoryLoad
from measurements.disk import HardDrive

#variabili Globali per semplificare la struttura del codice

isConnected = False
connectionThread = threading.Event()

with open("./config.json") as f:
    config = json.load(f)
    f.close()

mqttClient = None
shadowClient = None

#Parametri di funzionamento e connessione ad AWS Iot
device_id = config["thingName"]
endpoint = config["endpoint"]
rootCAPath = config["rootCAPath"]
certificatePath = config["certificatePath"]
privateKeyPath = config["privateKeyPath"]
port = 8883
shadow_clientId = device_id + "_shadow"
thingName = config["thingName"]

parametri = config["parameters"]["telemetry_measurements"]

# Chiusura della connessioe (se attiva) quando CTRL-C
def signal_handler(sig, frame):
    print("Chiusura in corso")
    connectionThread.set()
    if isConnected:
        print("Disconnessione in corso")
        mqttClient.disconnect()
        print("Disconnesso")
    sys.exit(0)


# callback chiamata quando il dispositivo rileva la connessione ad AWS IoT
def connected(mid, data):
    print(mid)
    global isConnected
    isConnected = True
    connectionThread.set()
    #inizialize shadow 
    shadowInitialize()

# callback chiamata quando il dispositivo rileva la mancanza di connessione ad AWS IoT
# avvia il thread di tentativo di riconnessione ogni 30s
def disconnessoAInternet():
    global isConnected
    isConnected = False 
    print("Errore nella connessione")
    connectionThread.clear()
    threading.Timer(30, connect, [connectionThread]).start()

# funzione per tentare la connessione ad AWS IoT
# se non è presente la connessione riprova dopo 30s
def connect():
    mqttClient.connectAsync(ackCallback=connected)
    try:
        if not connectionThread.is_set():
            mqttClient.connectAsync(ackCallback=connected)
    except:
        print("Nessuna connessione a internet")
        # call connect() again in 30 seconds
        threading.Timer(30, connect).start()


def liveData(misurazioniDaEffettuare, tempoAggiornamento=10):
    """Invia una misurazione ad AWS IoT ogni tempoAggiornamento

    Args:
        misurazioniDaEffettuare (List): Array con le misurazioni da effetuare. 
                                        Possibili misurazioni "net_io", "cpu_load", "disk_space", "memory_load"
        tempoAggiornamento (int): tempo di aggiornamento in secondi. Se non specificato impostato a 10s
    """
    netstat = NetMeasurement()
    cpuMemStat = CpuMemoryLoad()
    timestamp = NtpSyncTime()

    misurazione = {"device_id" : device_id,
                    "measurement_type" : [],
                    "measurement": {
                        "iso_timestamp": None,
                        "unix_timestamp": None}
    }

    while True:
        misurazione["measurement_type"].clear()
        misurazione["measurement"] = {
            "iso_timestamp": timestamp.getIsoTimestamp(),
            "unix_timestamp": timestamp.getInfluxTimestamp()
        }

        if(misurazioniDaEffettuare["cpu_load"] == "Enabled"):
            misurazione["measurement_type"].append("cpu_load")
            misurazione["measurement"]["cpu_load"] = cpuMemStat.getLiveCpuData()


        if(misurazioniDaEffettuare["net_io"] == "Enabled"):
            misurazione["measurement_type"].append("net_io")
            misurazione["measurement"]["net_io"] = netstat.getData()


        if(misurazioniDaEffettuare["disk_space"] == "Enabled"):
            misurazione["measurement_type"].append("disk_space")
            misurazione["measurement"]["disk_space"] = HardDrive.getHarDriveUsage()


        if(misurazioniDaEffettuare["memory_load"] == "Enabled"):
            misurazione["measurement_type"].append("memory_load")
            misurazione["measurement"]["memory_load"] = cpuMemStat.getMemoryData()


        data = json.dumps(misurazione)
        mqttClient.publishAsync("pcTelemetry/{}/liveTelemetry".format(device_id), data, 1, ackCallback=pubackCallback())

        time.sleep(tempoAggiornamento)

# callback chiamata quando viene pubblicato un messaggio (eventualmente nella coda dei essaggi in mancanza di connessione)
def pubackCallback():
    print("pubblicato")


def detailData(misurazioniDaEffettuare, tempoAggiornamento=1):
    """Invia un array di 30 misurazioni ad AWS IoT, misurazioni effettuate ogni tempoAggiornamento

    Args:
        misurazioniDaEffettuare (List): Array con le misurazioni da effetuare. 
                                        Possibili misurazioni "net_io", "cpu_load", "disk_space", "memory_load"
        tempoAggiornamento (int, optional): tempo di aggiornamento in secondi per ogni misurazione. Defaults to 1.
    """
    netstat = NetMeasurement()
    cpuMemStat = CpuMemoryLoad()
    timestamp = NtpSyncTime()

    single_measurement = {
        "measurement_type": [],
        "measurement": {
            "iso_timestamp": None,
            "unix_timestamp": None            
        },
    }

    data_array = {
        "device_id": device_id
    }

    measurement_array=[]
    count = 0
    while True:
        single_measurement["measurement_type"].clear()
        single_measurement["measurement"] = {
            "iso_timestamp": timestamp.getIsoTimestamp(),
            "unix_timestamp": timestamp.getInfluxTimestamp()
        }

        if(misurazioniDaEffettuare["cpu_load"] == "Enabled"):
            single_measurement["measurement_type"].append("cpu_load")
            single_measurement["measurement"]["cpu_load"] = cpuMemStat.getDetailCpuData()

        if(misurazioniDaEffettuare["net_io"] == "Enabled"):
            single_measurement["measurement_type"].append("net_io")
            single_measurement["measurement"]["net_io"] = netstat.getData()
        

        if(misurazioniDaEffettuare["memory_load"] == "Enabled"):
            single_measurement["measurement_type"].append("memory_load")
            single_measurement["measurement"]["memory_load"] = cpuMemStat.getMemoryData()

        if(misurazioniDaEffettuare["battery"] == "Enabled"):
            single_measurement["measurement_type"].append("battery")


        measurement_array.append(copy.deepcopy(single_measurement))

        count += 1
        if count == 30:
            data_array["measurement_array"]=measurement_array
            fastdata = json.dumps(data_array)
            measurement_array.clear()
            mqttClient.publishAsync("pcTelemetry/{}/detailTelemetry".format(device_id), fastdata, 1, ackCallback=sentArray())
            count = 0

        time.sleep(tempoAggiornamento)

# callback chiamata quando viene pubblicato un array di misurazioni dalla funzione detailData
def sentArray():
    print("pubblicato detailTelemetry")


def shadowInitialize():
    updateDeviceFunctionalities(parametri)

# funzione di callback chiamata quando viene rilevato un delta nella shadow
def shadowDeltaCallback(payload, responseStatus, token):
    if(responseStatus == "accepted"):
        shadow = json.loads(payload)
        if "delta" in shadow["state"]:
            delta = shadow["state"]["delta"]
            updateDeviceFunctionalities(delta)
    elif (responseStatus != "rejected"):
        shadow = json.loads(payload)
        updateDeviceFunctionalities(shadow["state"])
    else:
        print("Richiesta shadow non accettata")
        print(responseStatus)

# abilita o disabilità funzionalità in base a quanto presente in delta
def updateDeviceFunctionalities(delta):
    shadowState = {
        "state" : {
            "reported": {
                "cpu_load": "Enabled",
                "memory_load": "Enabled",
                "disk_space": "Enabled",
                "net_io": "Enabled",
                "battery": "Disabled"
            }
        }       
    }

    for key, value in delta.items():
        parametri[key] = value
        shadowState["state"]["reported"][key] = value

    shadowStateJson = json.dumps(shadowState)
    shadowClient.shadowUpdate(shadowStateJson, shadowUpdateCallback, 5)

# callback chiamata dopo update della shadow.
# Se l'update è andato a buon fine, modifica il file config.json
# con l'attuale configurazione del dispositivo
def shadowUpdateCallback(payload, responseStatus, token):
    if(responseStatus == "accepted"):
        print("Shadow aggiornata")
        shadow = json.loads(payload)
        
        with open("./config.json", "w") as f:
            global config
            json.dump(config, f, indent=4)
            f.close()

        print(json.dumps(shadow["state"], indent=4))


#################
#### MAIN #######
#################
def main():
    signal.signal(signal.SIGINT, signal_handler)

    ########################
    ### #AWS IoT MQTT client setup
    global mqttClient
    mqttClient = AWSIoTMQTTClient(device_id)
    #Setup del client mqtt di aws iot
    mqttClient.disableMetricsCollection()
    mqttClient.configureEndpoint(endpoint, 8883)
    mqttClient.configureCredentials(
        rootCAPath,
        privateKeyPath,
        certificatePath,
    )

    # Backoff per riconnessione in caso di mancanza di connessione 
    mqttClient.configureAutoReconnectBackoffTime(1, 32, 20)
    # Coda dei messaggi in caso di mancanza di connessione 
    # Infinite offline Publish queueing
    mqttClient.configureOfflinePublishQueueing(-1)
    mqttClient.configureDrainingFrequency(10)  # Draining: 2 Hz
    mqttClient.configureConnectDisconnectTimeout(10)  # 10 sec
    mqttClient.configureMQTTOperationTimeout(5)  # 5 sec

    #callback in caso di mancanza di connessione
    mqttClient.onOffline = disconnessoAInternet


    #############################
    #### DEVICE SHADOW setup 

    global shadowClient
    shadow = AWSIoTMQTTShadowClient(shadow_clientId, awsIoTMQTTClient=mqttClient)

    shadowClient = shadow.createShadowHandlerWithName(thingName, True)

    shadowClient.shadowRegisterDeltaCallback(shadowDeltaCallback)



    #############################

    connect() #avvia il tentativo di connessione (ASYNC)

    ## Avvia 2 thread: 
    #   - uno pubblica una misurazione ogni 10s
    #   - uno pubblica un array di 30 misurazioni. Con una misurazione ogni secondo
    t1 = threading.Thread(target=detailData, args=(parametri, 1))
    t2 = threading.Thread(target=liveData, args=(parametri, 10))
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()