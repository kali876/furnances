from dataclasses import replace
from datetime import datetime
import json
import os
import logging
from sys import maxsize
import requests
import logging.handlers as handlers
import time

os.chdir("/root/furnances")

SERVER_URL = "192.168.9.100"
AUTH_TOKEN = "YWRtaW46d3lXYTJ4ODJ4eFQj"
headers = {"Authorization": f"Basic {AUTH_TOKEN}"}

def getCurrentTimestamp():
    timestamp = datetime.timestamp(datetime.now())
    return int(timestamp)

logFilename = f"bakings-script.log"

logger = logging.getLogger('furnances')

logFormatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
logger.setLevel(logging.INFO)

logHandler = logging.handlers.RotatingFileHandler(logFilename, maxBytes=100000000, backupCount=2)

logHandler.setFormatter(logFormatter)
logger.addHandler(logHandler)




class Thermometer:

    __id = None

    def __init__(self, id):
        self.__setId(id)

    def getId(self):
        return self.__id
    def __setId(self, id):
        self.__id = id
    
    def getTemperature(self):

        response = requests.get(
            f"http://{SERVER_URL}:8060/api/json/device/{str(self.getId())}/state",
            headers=headers,
            verify=False,
            timeout=10,
        )

        return float(json.loads(response.text)["Results"]["state"])

    def toJSON(self):

        json = {
            "id" : self.getId()
        }

        return json

class Heater:

    __id = None

    def __init__(self, id):
        self.__setId(id)

    def getId(self):
        return self.__id
    def __setId(self, id):
        self.__id = id

    def on(self):

        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getId())}/setValue/255",
            headers=headers,
            verify=False,
            timeout=10,
        )
        
    def off(self):

        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getId())}/setValue/0",
            headers=headers,
            verify=False,
            timeout=10,
        )

    def toJSON(self):

        json = {
            "id" : self.getId()
        }

        return json

class CyrcFan:

    __id = None

    def __init__(self, id):
        self.__setId(id)

    def getId(self):
        return self.__id
    def __setId(self, id):
        self.__id = id

    def on(self):

        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getId())}/setValue/1",
            headers=headers,
            verify=False,
            timeout=10,
        )
        
    def off(self):

        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getId())}/setValue/0",
            headers=headers,
            verify=False,
            timeout=10,
        )

    def status(self):
        response = requests.get(
            f"http://{SERVER_URL}:8060/api/json/device/{str(self.getId())}/state",
            headers=headers,
            verify=False,
            timeout=10,
        )
        return float(json.loads(response.text)["Results"]["state"])

    def toJSON(self):

        json = {
            "id" : self.getId()
        }

        return json

class ExhaustFan:
    __id = None

    def __init__(self, id):
        self.__setId(id)

    def getId(self):
        return self.__id

    def __setId(self, id):
        self.__id = id

    def on(self):
        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getId())}/setValue/1",
            headers=headers,
            verify=False,
            timeout=10,
        )

    def off(self):
        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getId())}/setValue/0",
            headers=headers,
            verify=False,
            timeout=10,
        )

    def toJSON(self):
        json = {
            "id": self.getId()
        }

        return json

class Furnance:

    __id = None
    __thermometers = None
    __heaters = None
    __cyrcfans = None
    __exhaustfans = None

    def __init__(self, id):
        self.__setId(id)
        self.__load()

    def getId(self):
        return self.__id
    def __setId(self, id):
        self.__id = id
    
    def getThermometers(self):
        return self.__thermometers
    def __setThermometers(self, thermometers):
        if self.__thermometers == None:
            self.__thermometers = []
        self.__thermometers = thermometers
    def __addThermometer(self, thermometer):
        if self.__thermometers == None:
            self.__thermometers = []
        self.__thermometers.append(thermometer)

    def getHeaters(self):
        return self.__heaters
    def __setHeaters(self, heaters):
        if self.__heaters == None:
            self.__heaters = []
        self.__heaters = heaters
    def __addHeater(self, heater):
        if self.__heaters == None:
            self.__heaters = []
        self.__heaters.append(heater)

    def getCyrcFans(self):
        return self.__cyrcfans
    def __setCyrcyFans(self, fans):
        if self.__cyrcfans == None:
            self.__cyrcfans = []
        self.__cyrcfans = fans
    def __addCyrcFans(self, fan):
        if self.__cyrcfans == None:
            self.__cyrcfans = []
        self.__cyrcfans.append(fan)

    def getExhaustFans(self):
        return self.__exhaustfans
    def __setExhaustFans(self, exfans):
        if self.__exhaustfans == None:
            self.__exhaustfans = []
        self.__exhaustfans = exfans
    def __addExhaustFans(self, exfan):
        if self.__exhaustfans == None:
            self.__exhaustfans = []
        self.__exhaustfans.append(exfan)

    def getTemperature(self):

        temperature = 0

        for thermometer in self.getThermometers():
            temperature = temperature + thermometer.getTemperature()

        temperature = temperature / len(self.getThermometers())

        temperature = round(temperature, 2)

        return temperature

    def heateron(self, power):
        heater = self.getHeaters()
        if power == 5:
            heater[0].on()
            logger.info(f"Turn ON heaters 5")
        elif power == 15:
            heater[1].on()
            logger.info(f"Turn ON heaters 15")
        elif power == 20:
            heater[2].on()
            logger.info(f"Turn ON heaters 20")
        elif power == 30:
            heater[3].on()
            logger.info(f"Turn ON heaters 30")
        elif power == 40:
            heater[4].on()
            logger.info(f"Turn ON heaters 40")

    def heateroff(self):
        for heater in self.getHeaters():
            heater.off()
        logger.info(f"Turn OFF heaters")

    def cyrcfanon(self):
        for cyrcefan in self.getCyrcFans():
            cyrcefan.on()
        logger.info(f"Turn ON cycle fan")
    def cyrcfanoff(self):
        for cyrcefan in self.getCyrcFans():
            cyrcefan.off()
        logger.info(f"Turn OFF cycle fans")

    def cyrcfanstatus(self):
        fan = 0
        for cyrcfan in self.getCyrcFans():
            fan = fan + cyrcfan.status()
            logger.info(f" Status wentyaltorów cyrk {cyrcfan.status()}....")

    def __load(self):

        file = open(f"furnances/furnance-{self.getId()}.json")

        data = json.load(file)

        for thermometerId in data["thermometers_ids"]:
            self.__addThermometer(Thermometer(thermometerId))
        for heatersId in data["heaters_ids"]:
            self.__addHeater(Heater(heatersId))
        for cyrcfanId in data["cyrc_fans_ids"]:
            self.__addCyrcFans(CyrcFan(cyrcfanId))
        for exhaustfanId in data["exhaust_fans_ids"]:
            self.__addExhaustFans(ExhaustFan(exhaustfanId))

    def toJSON(self):

        json = {
            "furnance_id" : self.getId(),
            "thermometers" : [thermometer.toJSON() for thermometer in self.getThermometers()],
            "heaters" : [heater.toJSON() for heater in self.getHeaters()],
            "cyrcfan" : [cyrcfan.toJSON() for cyrcfan in self.getCyrcFans()],

        }

        return json

class BakingStep:

    __stepNumber = None
    __startTemperature = None
    __endTemperature = None
    __duration = None

    def __init__(self, *args):
        if len(args) == 1:
            self.__setStepNumber(args[0]["step_number"])
            self.__setStartTemperature(args[0]["start_temperature"])
            self.__setEndTemperature(args[0]["end_temperature"])
            self.__setDuration(args[0]["duration"])
        else:
            self.__setStepNumber(args[0])
            self.__setStartTemperature(args[1])
            self.__setEndTemperature(args[2])
            self.__setDuration(args[3])

    def getStepNumber(self):
        return self.__stepNumber

    def __setStepNumber(self, number):
        self.__stepNumber = int(number)

    def getStartTemperature(self):
        return self.__startTemperature

    def __setStartTemperature(self, temperature):
        self.__startTemperature = int(temperature)
    
    def getEndTemperature(self):
        return self.__endTemperature

    def __setEndTemperature(self, temperature):
        self.__endTemperature = int(temperature)

    def getDuration(self):
        return self.__duration

    def __setDuration(self, timestamp):
        self.__duration = int(timestamp)

    def toJSON(self):

        json = {
            "step_number" : self.getStepNumber(),
            "start_temperature" : self.getStartTemperature(),
            "end_temperature" : self.getEndTemperature(),
            "duration" : self.getDuration(),
        }

        return json

class BakingProcess:

    __bakingSteps = None
    __furnance = None
    __startTime = None
    __processFileName = None

    def __init__(self, fileName):
        file = open(f"bakings/{fileName}")
        self.__setProcessFileName(fileName)
        self.__load(file)

    def getBakingSteps(self):
        return self.__bakingSteps

    def __setBakingSteps(self, steps):
        self.__bakingSteps = steps

    def __addBakingStep(self, step):
        if self.__bakingSteps == None:
            self.__bakingSteps = []
        self.__bakingSteps.append(step)

    def getCurrentTrend(self):
        currentStep = self.getCurrentStep()
        temperatureDifference = currentStep.getEndTemperature() - currentStep.getStartTemperature()
        if temperatureDifference >0:
            CurrentTrend = 1 # Grzanie
        elif temperatureDifference == 0:
            CurrentTrend = 0 # Utrzymanie
        elif temperatureDifference < 0:
            CurrentTrend = 2   #Chłodzenie
        # elif currentStep == len(self.getBakingSteps()):
        #      CurrentTrend = 3  # Ostatni etap chłodzenia
        return CurrentTrend

    def getFurnance(self):
        return self.__furnance

    def __setFurnance(self, furnance):
        self.__furnance = furnance


    def getStartTime(self):
        return self.__startTime

    def __setStartTime(self, time):
        self.__startTime = time

    def getProcessFileName(self):
        return self.__processFileName

    def __setProcessFileName(self, filename):
        self.__processFileName = filename

    def __load(self, file):

        data = json.load(file)

        for step in data["steps"]:
            self.__addBakingStep(BakingStep(step))

        self.getBakingSteps().sort(key=lambda x: x.getStepNumber(), reverse=False)

        self.__setFurnance(Furnance(data["furnance_id"]))
        
        self.__setStartTime(data["start_time"])

    def getCurrentStep(self):
        currentTime = getCurrentTimestamp()
        time = self.getStartTime()

        for step in self.getBakingSteps():
            if time <= currentTime <= (time + step.getDuration()):
                return step
            else:
                time = time + step.getDuration()

    def getStepByNumber(self, number):
        for step in self.getBakingSteps():
            if step.getStepNumber() == number:
                return step

    def getDesiredTemperature(self):

        currentStep = self.getCurrentStep()

        temperatureDifference = currentStep.getEndTemperature() - currentStep.getStartTemperature()

        temperaturePerSecond = temperatureDifference / currentStep.getDuration()

        currentStepStartTime = self.getStartTime()

        for seq in range(1, currentStep.getStepNumber()): 
            step = self.getStepByNumber(seq)
            currentStepStartTime = currentStepStartTime + step.getDuration()

        positionInCurrentStep = getCurrentTimestamp() - currentStepStartTime

        desiredTemperature = currentStep.getStartTemperature() + (positionInCurrentStep * temperaturePerSecond)

        desiredTemperature = round(desiredTemperature, 2)

        return desiredTemperature

    def isFinished(self):

        currentTime = getCurrentTimestamp()
        time = self.getStartTime()

        for step in self.getBakingSteps():
            time = time + step.getDuration()

        if currentTime >= time:
            return True

        return False

    def addToRaport(self, line):

        startDate = datetime.fromtimestamp(self.getStartTime())

        file = open(f"raports/{startDate}.csv", 'a+')
        file.write(f"{line}\n")
        file.close()

    def createFinalRaport(self):
        logger.info(f"Creating raport... TODO")

    def deleteProcessFile(self):
        logger.info(f"Deleting file ./bakings/{self.getProcessFileName()}")
        os.remove(f"./bakings/{self.getProcessFileName()}")

    def toJSON(self):

        json = {
            "furnance_id" : 1,
            "steps" : [step.toJSON() for step in self.getBakingSteps()],
            "start_time" : self.getStartTime()
        }

        return json

    def saveToFile(self):
        with open(f"bakings/furnance-1.json", "w+") as outfile:
            json.dump(self.toJSON(), outfile, indent=4, sort_keys=True)

def main():

    logger.info("==================================================")

    logger.info('START ITERATION')

    files = [file for file in os.listdir("./bakings") if file.endswith('.json')]

    for file in files:

        logger.info("==================================================")

        process = BakingProcess(file)

        logger.info(f"Start updating baking process in furnance {process.getFurnance().getId()}...")

        if process.isFinished() == True:
            logger.info(f"Process is finished!")
            process.getFurnance().heateroff()
            process.getFurnance().cyrcfanoff()
            process.createFinalRaport()
            process.deleteProcessFile()
            continue

        logger.info(f"Process is running")

        cyrcfanStatus = process.getFurnance().cyrcfanstatus()
        # if cyrcfanStatus < 1:
        #     process.getFurnance().cyrcfanon()

        currentTemperature = process.getFurnance().getTemperature()
        currentTrend = process.getCurrentTrend()
        stepsLeft = len(process.getBakingSteps()) - process.getCurrentStep().getStepNumber()

        logger.info(f"Current temperature in furnance : {currentTemperature}")

        desiredTemperature = process.getDesiredTemperature()

        logger.info(f"Desired temperature : {desiredTemperature}")
        differenceTemperature = currentTemperature - desiredTemperature


        if stepsLeft < 1 or differenceTemperature > 1:
            process.getFurnance().heateroff()
            break
        elif differenceTemperature <= 1 and differenceTemperature > -0.2 and currentTrend == 1:
            process.getFurnance().heateron(5)
        elif differenceTemperature < -0.2 and differenceTemperature > -0.8 and currentTrend == 1:
            process.getFurnance().heateron(15)
        elif differenceTemperature < -0.8 and differenceTemperature > -3 and currentTrend == 1:
            process.getFurnance().heateron(20)
        elif differenceTemperature < -3 and differenceTemperature > -5 and currentTrend == 1:
            process.getFurnance().heateron(30)
        elif differenceTemperature < -5 and differenceTemperature > -100 and currentTrend == 1:
            process.getFurnance().heateron(40)
        if differenceTemperature != 0 and differenceTemperature > -0.3 and currentTrend == 0:
            process.getFurnance().heateron(5)
        elif differenceTemperature < -0.3 and differenceTemperature > -1.5 and currentTrend == 0:
            process.getFurnance().heateron(15)
        elif differenceTemperature < -1.5 and differenceTemperature > -3 and currentTrend == 0:
            process.getFurnance().heateron(20)
        elif differenceTemperature < -3 and differenceTemperature > -5 and currentTrend == 0:
            process.getFurnance().heateron(30)
        elif differenceTemperature < -5 and differenceTemperature > -100 and currentTrend == 0:
            process.getFurnance().heateron(40)
        if differenceTemperature != 0 and differenceTemperature > -0.3 and currentTrend == 2:
            process.getFurnance().heateron(5)
        elif differenceTemperature < -0.3 and differenceTemperature > -1.5 and currentTrend == 2:
            process.getFurnance().heateron(15)
        elif differenceTemperature < -1.5 and differenceTemperature > -3 and currentTrend == 2:
            process.getFurnance().heateron(20)
        elif differenceTemperature < -3 and differenceTemperature > -5 and currentTrend == 2:
            process.getFurnance().heateron(30)
        elif differenceTemperature < -5 and differenceTemperature > -100 and currentTrend == 2:
            process.getFurnance().heateron(40)


        currentDate = datetime.fromtimestamp(getCurrentTimestamp())

        raportLine = f"{currentDate};{currentTemperature};{desiredTemperature};"

        raportLine = raportLine.replace(".", ",")

        process.addToRaport(raportLine)

main()
time.sleep(10)
main()
time.sleep(10)
main()
time.sleep(10)
main()
time.sleep(10)
main()
time.sleep(10)
main()
