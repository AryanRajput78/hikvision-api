from django.http import Http404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import userDetails, deviceDetails

from requests.auth import HTTPDigestAuth

import os
import json
import logging
import requests
import datetime
import xmltodict
import pandas as pd

# Create your views here.

# Login credentials for the devices. Hide this after development. (Development Done.)
cred = {
    "user": "admin",
    "password": "a1234@4321",
}

# Log file initialization for keeping track of the files.
logging.basicConfig(
    filename="./logs.log", format="%(asctime)s %(message)s", filemode="w"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# API to check if the device is online or not. (Development Done.)
@api_view(['GET'])
def checkOnline(request):
    # df = pd.read_excel('./constant/devices.xls')
    data = deviceDetails.objects.all()
    deviceSerial = []
    for d in data:
        url = "http://" + str(d.ip)
        firmware = ""
        try:
            response = ""
            response = requests.get(f"{url}/ISAPI/Security/userCheck", auth=HTTPDigestAuth(
                cred['user'], cred["password"]), headers={}, data={}, timeout=0.1)
            response.raise_for_status()
            if response.status_code == 200:
                # print(f'Authentication for {url} successful.')
                status = 'Online'
                resp = requests.get(f"{url}/ISAPI/System/deviceinfo",
                                    auth=HTTPDigestAuth(cred['user'], cred["password"]))
                if resp.status_code == 200:
                    data = xmltodict.parse(resp.text)
                    data = data['DeviceInfo']
                    model = data['model']
                    serialNo = data['serialNumber']
                    firmware = model.replace(
                        " ", "") + serialNo.replace(" ", "")
                    resp.close()
                    logging.info(f"Device {d.ip} - Online.")
                    # print(f'Fetched System info for {url}.')
                else:
                    logging.info(f"Device {d.ip} - Unable to fetch information.")
            else:
                logging.info(f"Device {d.ip} - Authentication failed.")    
        except Exception as e:
            status = 'Offline'
            logging.info(f"Device - {d.ip} - Offline.")
        deviceSerial.append((firmware, url, status))
        query = deviceDetails.objects.get(pk=d.id)
        query.status = status
        query.save()
    print(deviceSerial)
    return Response(deviceSerial)

# API to get count of User, Cards and Face registered on the device. (Development Done.)
@api_view(['GET'])
def getCount(request):
    data = deviceDetails.objects.all()
    headers = {}
    payload = {}
    info = []
    response =""
    url_col_name = {
        ("/ISAPI/AccessControl/UserInfo/Count?format=json", "User", "userNumber"),
        ("/ISAPI/AccessControl/CardInfo/Count?format=json", "Card", "cardNumber"),
        ("/ISAPI/Intelligent/FDLib/Count?format=json&FDID=1&faceLibType=blackFD",
         "Face", "recordDataNumber")
    }
    # for d in data:
    #     print(d.ip, d.status)
    for d in data:
        count = {}
        count['IP'] = d.ip
        count['Status'] = d.status
        if d.status != "Offline":
            for i in url_col_name:
                url = "http://"+ d.ip + i[0]
                count[f"{i[1]}Count"] = ""
                # To obtain the Number of Users, Face, Cards registered on the device.
                try:
                    response = requests.get(url, auth=HTTPDigestAuth(
                        cred["user"], cred["password"]), headers=headers, data=payload, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if (i[1] != 'Face'):
                            data = data[f"{i[1]}InfoCount"]
                            count[f"{i[1]}Count"] = data[f"{i[2]}"]
                        else:
                            count["FaceCount"] = data['recordDataNumber']
                        response.close()
                except Exception as e:
                    if response != "":
                        response.close()
                finally:
                    if response != "":
                        response.close()
        info.append(count)
    return Response(info)
 
# API to get the registered User Details on the device. (Development Done.)
@api_view(['GET'])
def getUsers(request):
    data = deviceDetails.objects.all()
    info = []
    
    for d in data:
        start = datetime.datetime.now()
        searchPosition = 0
        users ={}
        users['IP'] = d.ip
        users['status'] = d.status
        if (d.status != "Offline"):
            url = "http://" + d.ip + "/ISAPI/AccessControl/UserInfo/Search?format=json"
            headers = {
                'Content-Type': 'application/json'
            }
            while True:
                payload = json.dumps({
                            "UserInfoSearchCond": {
                                "searchID": "1",
                                "maxResults": 30,
                                "searchResultPosition": searchPosition
                            }
                        })
                response = requests.post(url, auth=HTTPDigestAuth(
                            cred["user"], cred["password"]), headers=headers, data=payload, timeout=5)
                if response.status_code == 200:
                    data = response.json()['UserInfoSearch']
                    if data['responseStatusStrg'] == "OK" or data['responseStatusStrg'] == "MORE":
                        for uinfo in data['UserInfo']:
                            if uinfo['employeeNo']:
                                userTemplate = json.loads("""{
                                                    "UserInfo": {
                                                        "employeeNo": "",
                                                        "name": "",
                                                        "userType": "",
                                                        "gender": "",
                                                        "localUIRight": "",
                                                        "maxOpenDoorTime": 0,
                                                        "Valid": "",
                                                        "doorRight": "",
                                                        "RightPlan": "",
                                                        "userVerifyMode": "",
                                                        "CardInfo": "",
                                                        "Photo": ""
                                                    }
                                                }""")
                                for key in userTemplate["UserInfo"].keys():
                                    if key in uinfo.keys():
                                        userTemplate["UserInfo"][key] = uinfo[key]
                                    users[uinfo['employeeNo']] = userTemplate
                        if data['responseStatusStrg'] == "OK":
                            break
                        searchPosition += int(data['numOfMatches'])
                    if data['responseStatusStrg'] == "NO MATCH" or searchPosition > int(data['totalMatches']):
                        break
                    response.close()
                else:
                    if response != "":
                        response.close()
        info.append(users)
    end = datetime.datetime.now()
    logging.info(f"Time taken to fetch users - {end - start}")
    return Response(info)

# Function to check if the user exists or not on the device.
def checkUser(ip, id):
    url = "http://" + ip + "/ISAPI/AccessControl/UserInfo/Search?format=json"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "UserInfoSearchCond": {
            "searchID": "1",
            "maxResults": 1,
            "searchResultPosition": 0,
            "fuzzySearch": str(id)
        }
    })
    response = ""
    try:
        response = requests.post(url, auth=HTTPDigestAuth(cred["user"], cred["password"]), headers=headers, data=payload, timeout=1)
        if response.status_code == 200:
            data = response.json()['UserInfoSearch']
            if data['responseStatusStrg'] == "OK" or data['responseStatusStrg'] == "MORE":
                response.close()
                return 'Exists'
            if data['responseStatusStrg'] == "NO MATCH":
                response.close()
                return "Doesnt Exist"
    except Exception as e:
        if response != "":
            response.close()
        return 'Error'
    finally:
        if response != "":
            response.close()

# API to add user template to the devices. (Partial Development Done. create, modify,) (Work on Image uploads.)
@api_view(['GET', 'DELETE'])
def addUserTemplate(request):
    data = request.data
    headers = {
        'Content-Type': 'application/json'
    }
    if request.method == "GET":
        for d in data:
            keys = d.keys() 
            for key in keys:
                response = ""
                if key.isdigit():
                    ip = d['IP']
                    temp = d[key].get('UserInfo')
                    enable = temp['Valid']['enable']
                    emp = temp['employeeNo']
                    found = checkUser(ip, emp)
                    types = 'Modify' if found == 'Exists' else 'Record'
                    print(f"Get method - {request.method}")
                    template = json.dumps({
                        "UserInfo": {
                            "employeeNo": str(temp['employeeNo']),
                            "name": str(temp['name']),
                            "userType": str(temp['userType']).lower(),
                            "gender": str(temp['gender']).lower(),
                            "localUIRight": False,
                            "maxOpenDoorTime": 0,
                            "Valid": {
                                "enable": enable,
                                "beginTime": "2022-10-10T00:00:00",
                                "endTime": "2037-12-31T23:59:59",
                                "timeType": "local"
                            },
                            "doorRight": "1",
                            "RightPlan": [
                                {
                                    "doorNo": 1,
                                    "planTemplateNo": "1"
                                }
                            ],
                            "userVerifyMode": "",
                            "CardInfo": "",
                            "Photo": ""
                        }
                    })
                    if types == "Record":
                        url = "http://" + str(ip) + f"/ISAPI/AccessControl/UserInfo/{types}?format=json"
                        response = requests.post(url, auth=HTTPDigestAuth(cred["user"], cred["password"]), headers=headers, data=template, timeout=1)
                    else:
                        url = "http://" + str(ip) + f"/ISAPI/AccessControl/UserInfo/{types}?format=json"
                        response = requests.put(url, auth=HTTPDigestAuth(cred["user"], cred["password"]), headers=headers, data=template, timeout=1)
    if request.method == "DELETE":
        for d in data:
            keys = d.keys() 
            for key in keys:
                response = ""
                ip = d['IP']
                emp = d['UserInfoDelCond'].get('EmployeeNoList')[0]['employeeNo']
                found = checkUser(ip, emp)
                if found == "Exists":
                    template = json.dumps({
                        "UserInfoDelCond": {
                            "EmployeeNoList": [{
                                "employeeNo":  str(emp)
                            }]
                        }
                    }) 
                    url = "http://" + str(ip) + f"/ISAPI/AccessControl/UserInfo/Delete?format=json"
                    response = requests.put(url, auth=HTTPDigestAuth(cred["user"], cred["password"]), headers=headers, data=template, timeout=1)
                    print(response.text)
                else:
                    print('Employee Does not exist.')
                break
        logging.info(f"(addCardInfo) Response -> {response}")
    return Response("Success")
