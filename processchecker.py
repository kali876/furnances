
from datetime import datetime
import json
import os
import requests
import time

os.chdir("/root/furnances")

SERVER_URL = "192.168.9.100"
AUTH_TOKEN = "YWRtaW46d3lXYTJ4ODJ4eFQj"
headers = {"Authorization": f"Basic {AUTH_TOKEN}"}

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
    __furnance_id = None
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



def processchecker():

    files = [file for file in os.listdir("./furnances") if file.endswith('.json')]
    for file in files:
        ampio=Furnances(file)
        process_already_exist = ampio.isProcessExist()
        if process_already_exist == False:
            checked_cycle = ampio.getCheckedCycle()
            proces_start = ampio.getProcessStart()
            if proces_start == True and checked_cycle != None:
                ampio.savefile()





processchecker()