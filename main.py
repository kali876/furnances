from dataclasses import replace
from datetime import datetime
import json
import os
import logging
import requests


SERVER_URL = "192.168.9.100"
AUTH_TOKEN = "YWRtaW46d3lXYTJ4ODJ4eFQj"
headers = {"Authorization": f"Basic {AUTH_TOKEN}"}

logging.basicConfig(filename='bakings-script.log', level=logging.DEBUG, format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', datefmt='%m-%d-%Y %I:%M:%S')

logging.info("==================================================")

logging.info('START ITERATION')

def getCurrentTimestamp():
    timestamp = datetime.timestamp(datetime.now())
    return int(timestamp)

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

        return int(json.loads(response.text)["Results"]["state"])

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

        pass

    def toJSON(self):

        json = {
            "id" : self.getId()
        }

        return json

class Furnance:

    __id = None
    __thermometers = None
    __heaters = None

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

    def getTemperature(self):

        temperature = 0

        for thermometer in self.getThermometers():
            temperature = temperature + thermometer.getTemperature()

        temperature = temperature / len(self.getThermometers())

        temperature = round(temperature, 2)

        return temperature

    def on(self):
        for heater in self.getHeaters():
            heater.on()
        logging.info(f"Turn ON heaters")


    def off(self):
        for heater in self.getHeaters():
            heater.off()
        logging.info(f"Turn OFF heaters")

    def __load(self):

        file = open(f"furnances/furnance-{self.getId()}.json")

        data = json.load(file)

        for thermometerId in data["thermometers_ids"]:
            self.__addThermometer(Thermometer(thermometerId))
        for heatersId in data["heaters_ids"]:
            self.__addHeater(Heater(heatersId))

    def toJSON(self):

        json = {
            "furnance_id" : self.getId(),
            "thermometers" : [thermometer.toJSON() for thermometer in self.getThermometers()],
            "heaters" : [heater.toJSON() for heater in self.getHeaters()],
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
        logging.info(f"Creating raport... TODO")

    def deleteProcessFile(self):
        logging.info(f"Deleting file ./bakings/{self.getProcessFileName()}")
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

    files = [file for file in os.listdir("./bakings") if file.endswith('.json')]

    for file in files:

        logging.info("==================================================")

        process = BakingProcess(file)

        logging.info(f"Start updating baking process in furnance {process.getFurnance().getId()}...")

        if process.isFinished() == True:
            logging.info(f"Process is finished!")
            process.getFurnance().off()
            process.createFinalRaport()
            process.deleteProcessFile()
            continue

        logging.info(f"Process is running")

        currentTemperature = process.getFurnance().getTemperature()

        logging.info(f"Current temperature in furnance : {currentTemperature}")

        desiredTemperature = process.getDesiredTemperature()

        logging.info(f"Desired temperature : {desiredTemperature}")

        if currentTemperature < desiredTemperature:
            process.getFurnance().on()
        elif currentTemperature >= desiredTemperature:
            process.getFurnance().off()

        currentDate = datetime.fromtimestamp(getCurrentTimestamp())

        raportLine = f"{currentDate};{currentTemperature};{desiredTemperature};"

        raportLine = raportLine.replace(".", ",")

        process.addToRaport(raportLine)

main()