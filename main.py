from dataclasses import replace
from datetime import datetime
import json
import os
import logging
from sys import maxsize
import requests
import logging.handlers as handlers
import time
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

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


class Mail:
    #__id = None
    __server_id = None
    __server_address = None
    __recipients = None
    __sender = None
    __subject = None
    __login = None
    __pass = None
    __message = None
    __attachment = None

    def __init__(self):
        self.__load()

    #def getServers(self):
    #    return self.__server_id

    #def __setServers(self, servers):
    #    if self.__server_id == None:
    #        self.__server_id = []
    #    self.__server_id = servers

    def getServerAddress(self):
        return self.__server_address

    def __setServerAddress(self, smtp):
        self.__server_address = smtp

    def getReceipient(self):
        return self.__recipients

    def __setReceipient(self, receipient):
        self.__recipients = receipient

    def __addReceipient(self, receipient):
        if self.__recipients == None:
            self.__recipients = []
        self.__recipients.append(receipient)

    def getSender(self):
        return self.__sender

    def __setSender(self, sender):
        self.__sender = sender

    def getLogin(self):
        return self.__login

    def __setLogin(self, login):
        self.__login = login

    def getPass(self):
        return self.__pass

    def __setPass(self, passwd):
        self.__pass = passwd

    def __load(self):

        file = open(f"mail/mailserver.json")

        data = json.load(file)

        #self.__setServers = data["server_id"]
        self.__setServerAddress(data["server_address"])
        self.__setReceipient(data["recipients"])
        self.__setSender(data["sender"])
        self.__setLogin(data["login"])
        self.__setPass(data["pass"])

    def send_mail(self, subject, message, file):
        msg = MIMEMultipart()
        msg['From'] = self.getSender()
        msg['To'] = self.getReceipient()
        #msg['Date'] = datetime.timestamp(datetime.now())
        msg['Subject'] = subject

        print(f"sub: {subject}, mes: {message}, file: {file} receipient:{self.getReceipient()} sender: {self.getSender()}")

        msg.attach(MIMEText(message))
        filename = f"Raport_{datetime.fromtimestamp(BakingProcess.getStartTime())}"
        attachment = open(file, 'rb')
        attachment_package = MIMEBase('application', 'octet-stream')
        attachment_package.set_payload(attachment.read())
        encoders.encode_base64(attachment_package)
        attachment_package.add_header('Content-Disposition', "attachment; filename= " + filename)
        msg.attach(attachment_package)

        text = msg.as_string()

        context = ssl.create_default_context()
        TIE_server = smtplib.SMTP(self.getServerAddress(), 587)
        TIE_server.ehlo()
        TIE_server.starttls(context=context)
        TIE_server.ehlo()
        TIE_server.login(self.getLogin(), self.getPass())
        TIE_server.sendmail(self.getSender(), self.getReceipient(), text)
        TIE_server.quit()


class Messages:
    __id = None
    __Steps = None
    __CurrentStep = None
    __CurrentTemp = None
    __DesireTemp = None
    __StepTimeLeft = None
    __ProcessTimeLeft = None

    def __init__(self, *args):
        self.__setId(args[0]["message_id"])
        self.__setSteps(args[0]["message_steps"])
        self.__setCurrentStep(args[0]["message_current_step"])
        self.__setCurrentTemp(args[0]["message_current_temp"])
        self.__setDesireTemp(args[0]["message_desire_temp"])
        self.__setStepTimeLeft(args[0]["message_step_time_left"])
        self.__setProcessTimeLeft(args[0]["message_process_time_left"])

    def getId(self):
        return self.__id

    def __setId(self, id):
        self.__id = id

    def getSteps(self):
        return self.__Steps

    def __setSteps(self, steps):
        self.__Steps = steps

    def getCurrentStep(self):
        return self.__setCurrentStep

    def __setCurrentStep(self, step):
        self.__setCurrentStep = step

    def getCurrentTemp(self):
        return self.__setCurrentTemp

    def __setCurrentTemp(self, temp):
        self.__setCurrentTemp = temp

    def getDesireTemp(self):
        return self.__setDesireTemp

    def __setDesireTemp(self, temp):
        self.__setDesireTemp = temp

    def getStepTimeLeft(self):
        return self.__setStepTimeLeft

    def __setStepTimeLeft(self, st_time):
        self.__setStepTimeLeft = st_time

    def getProcessTimeLeft(self):
        return self.__setProcessTimeLeft

    def __setProcessTimeLeft(self, pr_time):
        self.__setProcessTimeLeft = pr_time

    def showsteps(self, steps):
        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getSteps())}/setText/{steps}",
            headers=headers,
            verify=False,
            timeout=10,
        )

    def showcurrentstep(self, step):
        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getCurrentStep())}/setText/{step}",
            headers=headers,
            verify=False,
            timeout=10,
        )

    def showcurrenttemp(self, ctemp):
        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getCurrentTemp())}/setText/{ctemp}",
            headers=headers,
            verify=False,
            timeout=10,
        )

    def showdesiretemp(self, dtemp):
        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getDesireTemp())}/setText/{dtemp}",
            headers=headers,
            verify=False,
            timeout=10,
        )

    def showsteptimeleft(self, stime):
        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getStepTimeLeft())}/setText/{stime}",
            headers=headers,
            verify=False,
            timeout=10,
        )

    def showprocesstimeleft(self, ptime):
        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getProcessTimeLeft())}/setText/{ptime}",
            headers=headers,
            verify=False,
            timeout=10,
        )


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
            "id": self.getId()
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
            "id": self.getId()
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
        return int(json.loads(response.text)["Results"]["state"])

    def toJSON(self):
        json = {
            "id": self.getId()
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

    def status(self):
        response = requests.get(
            f"http://{SERVER_URL}:8060/api/json/device/{str(self.getId())}/state",
            headers=headers,
            verify=False,
            timeout=10,
        )
        return int(json.loads(response.text)["Results"]["state"])

    def toJSON(self):
        json = {
            "id": self.getId()
        }

        return json


class Valve:
    __id = None
    __name = None
    __id_on = None
    __id_off = None
    __id_stat_on = None
    __id_stat_off = None

    def __init__(self, *args):
        if len(args) == 1:
            self.__setId(args[0]["valve_id"])
            self.__setName(args[0]["valve_name"])
            self.__setTurnOnFlag(args[0]["open_valve"])
            self.__setTurnOffFlag(args[0]["close_valve"])
            self.__setOnFlag(args[0]["open_status"])
            self.__setOffFlag(args[0]["close_status"])
        else:
            self.__setId(args[0])
            self.__setName(args[1])
            self.__setTurnOnFlag(args[0])
            self.__setTurnOffFlag(args[1])
            self.__setOnFlag(args[2])
            self.__setOffFlag(args[3])

    def getId(self):
        return self.__id

    def __setId(self, id):
        self.__id = id

    def getName(self):
        return self.__name

    def __setName(self, name):
        self.__name = name

    def getTurnOnFlag(self):
        return self.__id_on

    def __setTurnOnFlag(self, id_on):
        self.__id_on = id_on

    def getTurnOffFlag(self):
        return self.__id_off

    def __setTurnOffFlag(self, id_off):
        self.__id_off = id_off

    def getOnFlag(self):
        return self.__id_stat_on

    def __setOnFlag(self, id_stat_on):
        self.__id_stat_on = id_stat_on

    def getOffFlag(self):
        return self.__id_stat_off

    def __setOffFlag(self, id_stat_off):
        self.__id_stat_off = id_stat_off

    def on(self):
        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getTurnOnFlag())}/setValue/255",
            headers=headers,
            verify=False,
            timeout=10,
        )

    def off(self):
        requests.get(
            f"http://{SERVER_URL}:8060/api/set/{str(self.getTurnOffFlag())}/setValue/255",
            headers=headers,
            verify=False,
            timeout=10,
        )

    def status(self):
        on_status_request = requests.get(
            f"http://{SERVER_URL}:8060/api/json/device/{str(self.getOnFlag())}/state",
            headers=headers,
            verify=False,
            timeout=10,
        )

        off_status_request = requests.get(
            f"http://{SERVER_URL}:8060/api/json/device/{str(self.getOffFlag())}/state",
            headers=headers,
            verify=False,
            timeout=10,
        )
        on_status = int(json.loads(on_status_request.text)["Results"]["state"])
        off_status = int(json.loads(off_status_request.text)["Results"]["state"])

        if on_status != 0 and off_status == 0:
            status = 1  # Klapa otwarta
        elif on_status == 0 and off_status != 0:
            status = 2  # Klapa zamknięta
        elif on_status == 0 and off_status == 0:
            status = 3  # Klapa pomiędzy

        return status

    def toJSON(self):
        json = {
            "id": self.getId(),
            "valve_name": self.getName(),
            "open_valve": self.getTurnOnFlag(),
            "close_valve": self.getTurnOffFlag(),
            "open_status": self.getOnFlag(),
            "close_status": self.getOffFlag()
        }

        return json

    def __str__(self):
        return self.getName()


class Furnance:
    __id = None
    __thermometers = None
    __heaters = None
    __cyrcfans = None
    __exhaustfans = None
    __valves = None
    __messages = None

    def __init__(self, id):
        self.__setId(id)
        self.__load()

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

    def getValves(self):
        return self.__valves

    def __setValves(self, valves):
        if self.__valves == None:
            self.__valves = []
        self.__valves = valves

    def __addValve(self, valve):
        if self.__valves == None:
            self.__valves = []
        self.__valves.append(valve)

    def getMessages(self):
        return self.__messages

    def __setMessages(self, messages):
        if self.__messages == None:
            self.__messages = []
        self.__messages = messages

    def getValveByName(self, name):
        for valves in self.getValves():
            if valves.getName() == name:
                return valves

    def exhaustValveOpen(self):
        exhaustvalve = self.getValveByName("exhaust")
        exhaustvalve.on()
        logger.info(f"Zawór wydechowy jest otwierany...")

    def exhaustValveClose(self):
        exhaustvalve = self.getValveByName("exhaust")
        exhaustvalve.off()
        logger.info(f"Zawór wydechowy jest zamykany...")

    def exhaustValveStatus(self):
        status = 0
        exhaustvalve = self.getValveByName("exhaust")
        if exhaustvalve.status() == 1:
            status = 1
        elif exhaustvalve.status() == 2:
            status = 2
        elif exhaustvalve.status() == 3:
            status = 3
        return status

    def freshairValveOpen(self):
        freshairvalve = self.getValveByName("freshair")
        freshairvalve.on()
        logger.info(f"Świerze powietrze jest otwierane...")

    def freshairValveClose(self):
        freshairvalve = self.getValveByName("freshair")
        freshairvalve.off()
        logger.info(f"Świerze powietrze jest zamykane...")

    def freshairValveStatus(self):
        status = 0
        freshairvalve = self.getValveByName("freshair")
        if freshairvalve.status() == 1:
            status = 1
        elif freshairvalve.status() == 2:
            status = 2
        elif freshairvalve.status() == 3:
            status = 3
        return status

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
        elif power == 60:
            heater[5].on()
            logger.info(f"Turn ON heaters 60")

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
        fan = False
        for cyrcfan in self.getCyrcFans():
            if cyrcfan.status > 0 and fan == False:
                fan = True
            logger.info(f" Status wentyaltorów  cyrkulacyjnych {fan}....")
        return fan

    def exhaustfanon(self):
        for exhaustfan in self.getExhaustFans():
            exhaustfan.on()
        logger.info(f"Turn ON exhaust fan")

    def exhaustfanoff(self):
        for exhaustfan in self.getExhaustFans():
            exhaustfan.off()
        logger.info(f"Turn OFF exhaust fan")

    def exhaustfanstatus(self):
        fan = False
        for exhaustfan in self.getExhaustFans():
            if exhaustfan.status() > 0 and fan == False:
                fan = True
            # logger.info(f" Status wentyaltorów  weydechowych {fan}....")
        return fan

    def cyrcfanstatus(self):
        fan = 0
        for exhaustfan in self.getExhaustFans():
            fan = fan + exhaustfan.status()
            # logger.info(f" Status wentyaltorów  cyrkulacyjnych {fan}....")
        return fan

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
        for valve in data["valves"]:
            self.__addValve(Valve(valve))
        for messages in data["messages"]:
            self.__setMessages(Messages(messages))

    def toJSON(self):

        json = {
            "furnance_id": self.getId(),
            "thermometers": [thermometer.toJSON() for thermometer in self.getThermometers()],
            "heaters": [heater.toJSON() for heater in self.getHeaters()],
            "cyrcfan": [cyrcfan.toJSON() for cyrcfan in self.getCyrcFans()],
            "exhausfan": [exhaustfan.toJSON() for exhaustfan in self.getExhaustFans()],
            "valves": [valve.toJSON() for valve in self.getValves()],
            "messages": [messages.toJSON() for messages in self.getMessages()]
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
            "step_number": self.getStepNumber(),
            "start_temperature": self.getStartTemperature(),
            "end_temperature": self.getEndTemperature(),
            "duration": self.getDuration(),
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
        if temperatureDifference > 0:
            CurrentTrend = 1  # Grzanie
        elif temperatureDifference == 0:
            CurrentTrend = 0  # Utrzymanie
        elif temperatureDifference < 0:
            CurrentTrend = 2  # Chłodzenie
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

        self.getFurnance().on()

        # if self.getFurnance().cyrcfanstatus() == False: self.getFurnance().cyrcfanon()

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

    def getStepTimeLeft(self):
        currentTime = getCurrentTimestamp()
        currentstep = self.getCurrentStep()
        StepStartTime = self.getStartTime()

        for x in range(1, currentstep.getStepNumber()):
            step = self.getStepByNumber(x)
            StepStartTime = StepStartTime + step.getDuration()

        currentTimeLeft = (StepStartTime - currentTime) / 60
        currentTimeLeft = round(currentTimeLeft, 0)
        return currentTimeLeft

    def getProcesTimeLeft(self):
        currentTime = getCurrentTimestamp()
        time = self.getStartTime()

        for step in self.getBakingSteps():
            time = time + step.getDuration()

        processTimeLeft = (time - currentTime) / 60
        processTimeLeft = round(processTimeLeft, 0)
        return processTimeLeft

    def updatestatus(self, inprogress):
        if inprogress == True:
            self.getFurnance().getMessages().showsteps(len(self.getBakingSteps()))
            self.getFurnance().getMessages().showcurrentstep(self.getCurrentStep().getStepNumber())
            self.getFurnance().getMessages().showcurrenttemp(self.getFurnance().getTemperature())
            self.getFurnance().getMessages().showdesiretemp(self.getDesiredTemperature())
            self.getFurnance().getMessages().showsteptimeleft(self.getStepTimeLeft())
            self.getFurnance().getMessages().showprocesstimeleft(self.getProcesTimeLeft())
        else:
            self.getFurnance().getMessages().showsteps("----")
            self.getFurnance().getMessages().showcurrentstep("----")
            self.getFurnance().getMessages().showcurrenttemp("----")
            self.getFurnance().getMessages().showdesiretemp("----")
            self.getFurnance().getMessages().showsteptimeleft("----")
            self.getFurnance().getMessages().showprocesstimeleft("----")

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
        startDate = datetime.fromtimestamp(self.getStartTime())
        message = f"Raport z procesu spiekania z dnia {startDate}"
        subject = f"Raport z procesu spiekania z dnia {startDate}"
        file = f"raports/{startDate}.csv"

        mail = Mail()
        mail.send_mail(subject, message, file)
        logger.info(f"Creating raport... TODO")

    def deleteProcessFile(self):
        logger.info(f"Deleting file ./bakings/{self.getProcessFileName()}")
        os.remove(f"./bakings/{self.getProcessFileName()}")

    def toJSON(self):

        json = {
            "furnance_id": 101,
            "steps": [step.toJSON() for step in self.getBakingSteps()],
            "start_time": self.getStartTime()
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
            process.getFurnance().exhaustfanoff()
            process.getFurnance().off()
            process.updatestatus(False)
            process.createFinalRaport()
            process.deleteProcessFile()
            continue

        logger.info(f"Process is running")
        logger.info(f"Obecny krok {process.getCurrentStep().getStepNumber()}...")
        process.updatestatus(True)

        currentTemperature = process.getFurnance().getTemperature()
        currentTrend = process.getCurrentTrend()
        stepsLeft = len(process.getBakingSteps()) - process.getCurrentStep().getStepNumber()

        logger.info(f"Current temperature in furnance : {currentTemperature}")

        desiredTemperature = process.getDesiredTemperature()

        logger.info(f"Desired temperature : {desiredTemperature}")
        differenceTemperature = currentTemperature - desiredTemperature

        if stepsLeft < 1:
            if differenceTemperature <= 0 and differenceTemperature > -3:
                print("DO NOTHIK")
            elif differenceTemperature <= -3 and differenceTemperature >= -10:
                if process.getFurnance().exhaustfanstatus() == True: process.getFurnance().exhaustfanoff()
                if process.getFurnance().exhaustValveStatus() != 1: process.getFurnance().exhaustValveOpen()
                if process.getFurnance().freshairValveStatus() != 1: process.getFurnance().freshairValveOpen()
            elif differenceTemperature < -10 and differenceTemperature > -11:
                print("DO NOTHIK")
            elif differenceTemperature <= -11:
                if process.getFurnance().exhaustfanstatus() == True: process.getFurnance().exhaustfanoff()
                if process.getFurnance().exhaustValveStatus() != 2: process.getFurnance().exhaustValveClose()
                if process.getFurnance().freshairValveStatus() != 1: process.getFurnance().freshairValveOpen()
            else:
                # if process.getFurnance().exhaustfanstatus() == False : process.getFurnance().exhaustfanon()
                if process.getFurnance().exhaustValveStatus() != 1: process.getFurnance().exhaustValveOpen()
                if process.getFurnance().freshairValveStatus() != 1: process.getFurnance().freshairValveOpen()
        elif stepsLeft >= 1:
            if process.getFurnance().exhaustfanstatus() == True: process.getFurnance().exhaustfanoff()
            if process.getFurnance().exhaustValveStatus() != 2: process.getFurnance().exhaustValveClose()
            if process.getFurnance().freshairValveStatus() != 2: process.getFurnance().freshairValveClose()

        if stepsLeft < 1 or differenceTemperature > 1:
            process.getFurnance().heateroff()
        elif differenceTemperature <= 1 and differenceTemperature > -0.2 and currentTrend == 1:
            process.getFurnance().heateron(5)
        elif differenceTemperature <= -0.2 and differenceTemperature > -0.7 and currentTrend == 1:
            process.getFurnance().heateron(15)
        elif differenceTemperature <= -0.7 and differenceTemperature > -2 and currentTrend == 1:
            process.getFurnance().heateron(20)
        elif differenceTemperature <= -2 and differenceTemperature > -3.5 and currentTrend == 1:
            process.getFurnance().heateron(30)
        elif differenceTemperature <= -3.5 and differenceTemperature > -5 and currentTrend == 1:
            process.getFurnance().heateron(40)
        elif differenceTemperature <= -5 and differenceTemperature > -100 and currentTrend == 1:
            process.getFurnance().heateron(60)
        elif differenceTemperature <= 0.5 and differenceTemperature > -0.1 and currentTrend == 0:
            process.getFurnance().heateron(5)
        elif differenceTemperature <= -0.1 and differenceTemperature > -1 and currentTrend == 0:
            process.getFurnance().heateron(15)
        elif differenceTemperature <= -1 and differenceTemperature > -3 and currentTrend == 0:
            process.getFurnance().heateron(20)
        elif differenceTemperature <= -3 and differenceTemperature > -5 and currentTrend == 0:
            process.getFurnance().heateron(30)
        elif differenceTemperature <= -5 and differenceTemperature > -100 and currentTrend == 0:
            process.getFurnance().heateron(40)
        elif differenceTemperature <= 1 and differenceTemperature > -0.3 and currentTrend == 2:
            process.getFurnance().heateron(5)
        elif differenceTemperature < -0.3 and differenceTemperature > -1.5 and currentTrend == 2:
            process.getFurnance().heateron(15)
        elif differenceTemperature < -1.5 and differenceTemperature > -3 and currentTrend == 2:
            process.getFurnance().heateron(20)
        elif differenceTemperature < -3 and differenceTemperature > -5 and currentTrend == 2:
            process.getFurnance().heateron(30)
        elif differenceTemperature < -5 and differenceTemperature > -100 and currentTrend == 2:
            process.getFurnance().heateron(40)
        else:
            process.getFurnance().heateroff()

        currentDate = datetime.fromtimestamp(getCurrentTimestamp())

        raportLine = f"{currentDate};{currentTemperature};{desiredTemperature};"

        raportLine = raportLine.replace(".", ",")

        process.addToRaport(raportLine)


main()
time.sleep(9)
main()
time.sleep(9)
main()
time.sleep(9)
main()
time.sleep(9)
main()
time.sleep(9)
main()
