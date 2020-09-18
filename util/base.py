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
    def __init__(self,url,proto):
        channel = grpc.insecure_channel(url)
        # 导入pb2,pb2_grpc
        self.pb2_grpc = importlib.import_module('pb2.' + proto + '_pb2_grpc')
        self.pb2 = importlib.import_module('pb2.' + proto + '_pb2')
        # 获取pb2_grpc文件的具体内容
        self.pb2_grpc_path = self.pb2_grpc.__file__
        self.pb2_grpc_data = self.__get_pb2_grpc__()
        # 获取stub服务名称
        self.server = self.__get_server__()
        # 创建stub服务
        self.stub = getattr(self.pb2_grpc, self.server)(channel)

    def __get_server__(self):
        """ 正则提取stub服务名称 """
        pattern = 'class (.+?Stub)\\(object\\):'
        try:
            cl = re.findall(pattern,self.pb2_grpc_data)
            if len(cl) != 1:
                raise 'stub服务提取失败'
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
        pattern = self.server.replace('Stub','')+ '/' + rpc + '\',\n[\\s\\S]*?request_serializer=([\\s\\S]*?),\n'
        try:
            rq = re.findall(pattern, self.pb2_grpc_data)
            if len(rq) != 1:
                raise 'request_serializer提取失败'
        except Exception as e:
            print('生成的pb2_grpc文件中的rq数量错误:', repr(e))
            raise
        rq = rq[0].split('.')[:-1]
        return rq

    def __req_join__(self,key,value):
        """ 当rpc请求的message部分有嵌套调用时，重新组合传递的参数 """
        if isinstance(value,str):
            return str(key)+'=\''+str(value)+'\','
        else:
            return str(key)+'='+str(value)+','

    def __req_nest__(self,head_req,data):
        """ 判断rpc请求的message部分是否有嵌套调用，处理嵌套部分的参数 """
        is_d = False
        d_req = ''
        for i in list(data.keys()):
            if '@' in i:
                s_req = ''
                mgessage_func,item = i.split('.')
                mgessage_func = mgessage_func.replace('@','')
                for j in data[i]:
                    s_req += self.__req_join__(j,data[i][j])
                if head_req not in dir(self.pb2):
                    data[item] = 'self.pb2.' + mgessage_func + '(' + str(s_req[:-1]) + ')'
                else:
                    data[item] = str('self.pb2.'+head_req) + '.' + mgessage_func + '(' + str(s_req[:-1]) + ')'
                is_d = True
                d_req += str(item)+'='+str(data[item])+','
            else:
                d_req += self.__req_join__(i,data[i])
        return d_req[:-1],is_d
        

    def send(self, rpc, kwargs):
        """ 组合调用链，发出rpc请求 """
        # 通过调用的rpc接口名称去获取对应的请求参数
        call = ''
        is_nest = False
        req = self.__get_requeset__(rpc)
        head_req = req[0]
        # proto文件无调用关系时导入模块的属性需要特殊处理
        if req[0].replace('__','_') in self.pb2.__name__:
            req = req[1:]

        # 组合调用链
        for i in req:
            if call == '':
                call = "getattr(self.pb2,'" + i + "')"
            else:
                call = 'getattr(' + call + ',\'' + i + '\')'

        # message嵌套调用时候进行处理
        req, is_nest = self.__req_nest__(head_req,kwargs)

        # 开始调用，正式发出请求
        func = getattr(self.stub, rpc)

        if is_nest:
            response = func(eval(call+'('+req+')'))
        else:
            response = func(eval(call)(**kwargs))

        return response

