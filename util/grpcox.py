# coding=utf-8
import grpc
import importlib
import sys
import os
import re
import requests
import json

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
sys.path.append(curPath)

class BaseRpc(object):

    def __init__(self, host, path):
        self.host = host
        url = "http://localhost:6969/server/"+self.host+"/services"
        proto_list = self.find_proto(path)
        querystring = {"restart":"0"}
        r = requests.request("POST", url, files=proto_list, params=querystring)
        assert(r.status_code==200),"grpc服务链接错误"

    def find_proto(self, path):
        list_file = os.listdir(path)
        proto_list = []
        for file_name in list_file:
            if file_name.endswith('.proto'):
                proto_file = ('protos', (file_name,open(path+'/'+file_name,'rb')))
                proto_list.append(proto_file)
        return proto_list

    def send(self, services, request, message):
        headers = {
            'Content-Type': "application/json"
        }
        url = "http://localhost:6969/server/"+self.host+"/function/"+services+"."+request+"/invoke"
        message = json.dumps(message)
        response = requests.request("POST", url, data=message, headers=headers)
        data = response.json()
        return data['data']['result']


