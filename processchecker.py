
from datetime import datetime
import json
import os
import logging
import logging.handlers as handlers
import requests
from main import Furnance

os.chdir("/root/furnances")

SERVER_URL = "192.168.9.100"
AUTH_TOKEN = "YWRtaW46d3lXYTJ4ODJ4eFQj"
headers = {"Authorization": f"Basic {AUTH_TOKEN}"}

logFilename = f"bakings-script.log"
logger = logging.getLogger('furnances')

logFormatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
logger.setLevel(logging.INFO)

logHandler = logging.handlers.RotatingFileHandler(logFilename, maxBytes=100000000, backupCount=2)

logHandler.setFormatter(logFormatter)
logger.addHandler(logHandler)

class Cycle:
    __id = None

    def __init__(self, id):
        self.__setId(id)

    def getId(self):
        return self.__id

    def __setId(self, id):
        self.__id = id

class IsProces:
    __id = None

    def __init__(self, id):
        self.__setId(id)

    def getId(self):
        return self.__id

    def __setId(self, id):
        self.__id = id

class Furnances:
    __furnance = None
    __startTime = None
    __cycle = None
    __isproces = None

    def __init__(self, fileName):
        file = open(f"furnances/{fileName}")
        self.__setFurnanceFileName(fileName)
        self.__load(file)

    def getFurnanceFileName(self):
        return self.__processFileName

    def __setFurnanceFileName(self, filename):
        self.__processFileName = filename

    def getFurnance(self):
        return self.__furnance

    def __setFurnance(self, furnance):
        self.__furnance = furnance

    def getCycle(self):
        return self.__cycle

    def __setCycle(self, cycle):
        if self.__cycle == None:
            self.__cycle = []
        self.__cycle = cycle

    def __addCycle(self, cycle):
        if self.__cycle == None:
            self.__cycle = []
        self.__cycle.append(cycle)

    def getIsProcess(self):
        return self.__isproces

    def __setIsProcess(self, proces):
        if self.__isproces == None:
            self.__isproces = []
        self.__isproces = proces

    def __addIsProcess(self, proces):
        if self.__isproces == None:
            self.__isproces = []
        self.__isproces.append(proces)

    def __load(self, file):
        data = json.load(file)
        self.__setFurnance(data["furnance_id"])

        for cycleId in data["cycle_ids"]:
            self.__addCycle(Cycle(cycleId))
        for isprocess in data["isprocess"]:
            self.__addIsProcess(IsProces(isprocess))

    def getCheckedCycle(self):
        checked_cycle = 0
        for cycle in self.getCycle():
            checked_cycle = getstatus(cycle.getId())
            if checked_cycle == 255:
                return cycle.getId()
    def getProcessStart(self):
        proces_start = 0
        for start in self.getIsProcess():
            proces_start = proces_start + getstatus(start.getId())
        if proces_start == 510:
            return True
        else:
            return False
    def getProcessStop(self):
        proces_stop = 0
        for stop in self.getIsProcess():
            proces_stop = proces_stop + getstatus(stop.getId())
        if proces_stop == 0:
            return True
        else:
            return False
    def isProcessExist(self):
        existing_proces = os.path.isfile(f"./bakings/furnance-{self.getFurnance()}.json")
        return existing_proces

    def loadSchema(self, id):
        file = open(f"./cycle/{id}.json")
        data = json.load(file)
        steps = []
        for step in data["steps"]:
            steps.append(step)
        return steps

    def getCurrentTimestamp(self):
        timestamp = datetime.timestamp(datetime.now())
        return int(timestamp)

    def toJson(self):
        json = {
        "furnance_id": self.getFurnance(),
        "cycle": self.getCheckedCycle(),
        "start_time": self.getCurrentTimestamp(),
        "steps": self.loadSchema(self.getCheckedCycle())
        }
        return json


    def savefile(self):
        with open(f"bakings/furnance-{self.getFurnance()}.json", "w+") as outfile:
            json.dump(self.toJson(), outfile, indent=4, sort_keys=True)

def getstatus(id):
    response = requests.get(
        f"http://{SERVER_URL}:8060/api/json/device/{str(id)}/state",
        headers=headers,
        verify=False,
        timeout=10,
    )
    return int(json.loads(response.text)["Results"]["state"])

def setvalue(id, value):
    requests.get(
        f"http://{SERVER_URL}:8060/api/set/{str(id)}/setValue/{value}",
        headers=headers,
        verify=False,
        timeout=10,
    )

def pushnotifi(message):
    requests.get(
        f"http://{SERVER_URL}:8060/api/pushNotification/{message}",
        headers=headers,
        verify=False,
        timeout=10,
    )
def setFurnanceFans(id):
    furnance=Furnance(id)
    curent_temp = furnance.getTemperature()
    if curent_temp > 100:
        furnance.exhaustValveOpen()
        furnance.freshairValveOpen()
        furnance.cyrcfanon()
        furnance.exhaustfanon()
    else:
        furnance.heateroff()
        furnance.cyrcfanoff()
        furnance.exhaustfanoff()


def processchecker():

    files = [file for file in os.listdir("./furnances") if file.endswith('.json')]
    for file in files:
        furnance=Furnances(file)
        process_already_exist = furnance.isProcessExist()
        if process_already_exist == False:
            setFurnanceFans(furnance.getFurnance())
            checked_cycle = furnance.getCheckedCycle()
            proces_start = furnance.getProcessStart()
            if proces_start == True and checked_cycle != None:
                furnance.savefile()
                pushnotifi(f"Proces spiekania został uruchomiony")
        else:
            proces_stop = furnance.getProcessStop()
            if proces_stop == True:
                logger.info(f"Deleting file ./bakings/{file}")
                os.remove(f"./bakings/{file}")







processchecker()