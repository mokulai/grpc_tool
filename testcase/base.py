# coding=utf-8
import grpc
import importlib
import sys
import os
import re

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
sys.path.append(curPath)

class BaseRpc(object):
    def __init__(self,url,proto,path=''):
        channel = grpc.insecure_channel(url)
        if path:
            path = 'pb2.' + path + '.'
        # 导入pb2,pb2_grpc
        self.pb2_grpc = importlib.import_module(path + proto + '_pb2_grpc')
        self.pb2 = importlib.import_module(path + proto + '_pb2')
        # 获取pb2_grpc文件的具体内容
        self.pb2_grpc_path = self.pb2_grpc.__file__
        self.pb2_grpc_data = self.__get_pb2_grpc__()
        # 获取stub服务名称
        self.server = self.__get_server__()
        # 创建stub服务
        self.stub = getattr(self.pb2_grpc, self.server)(channel)

    def __get_server__(self):
        """ 正则提取stub服务名称 """
        pattern = 'class (.+?Stub)\(object\):'
        try:
            cl = re.findall(pattern,self.pb2_grpc_data)
            if len(cl) != 1:
                raise
        except Exception as e:
            print('生成的pb2_grpc文件中的stub数量错误:',repr(e))
            raise
        return cl[0]

    def __get_pb2_grpc__(self):
        """ 获取pb2_grpc文件内容，方便后续正则提取 """
        with open(self.pb2_grpc_path,'r') as f:
            data = f.read()
        return data

    def __get_requeset__(self,rpc):
        """ 正则提取要调用的rpc接口的request_serializer的值 """
        pattern = self.server.replace('Stub','')+ '/' + rpc + '\',\n[\s\S]*?request_serializer=([\s\S]*?),\n'
        try:
            rq = re.findall(pattern, self.pb2_grpc_data)
            if len(rq) != 1:
                raise
        except Exception as e:
            print('生成的pb2_grpc文件中的rq数量错误:', repr(e))
            raise
        rq = rq[0].split('.')[:-1]
        return rq

    def send(self, rpc, kwargs):
        """ 组合调用链，发出rpc请求 """
        # 通过调用的rpc接口名称去获取对应的请求参数
        call = ''
        req = self.__get_requeset__(rpc)
        # proto文件无调用关系时导入模块的属性需要特殊处理
        if req[0].replace('__','_') in self.pb2.__name__:
            req = req[1:]
        # 组合调用链
        for i in req:
            if call == '':
                call = "getattr(self.pb2,'" + i + "')"
            else:
                call = 'getattr(' + call + ',\'' + i + '\')'
        call = 'getattr(self.stub, rpc)(' + call + '(**kwargs))'
        print(call)
        # 正式发出请求
        response = eval(call)
        return response

