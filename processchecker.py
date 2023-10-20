
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

        checked_cycle = False

        for cycle in self.getCycle():
            checked_cycle = getstatus(cycle.getId())
            if checked_cycle == True:
                print(checked_cycle)
                return checked_cycle

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

