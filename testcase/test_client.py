from __future__ import print_function
import logging
import pytest
import grpc
import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(curPath)

from base import BaseRpc

class TestHello(object):

    @pytest.fixture(params=[{"name":"a"}])
    def name(self, request):
        return request.param

    def test_hello(self,name):
        hello = BaseRpc('localhost:50051', 'helloworld',path='hello')
        r = hello.send('SayHello', name)
        print(r)

    def test_hello2(self, name):
        hello = BaseRpc('localhost:50051', 'hello',  path='hello2')
        r = hello.send('SayHello', name)
        print(r)



# #
# # name = {"enabled": 10}
# # hello = BaseRpc('0.0.0.0:2900', 'camp_app' , path='camp.api.proto.app_boss.v1.app')
# # print(hello.__get_server__())
# # r = hello.send('List', name)
# # print(r)
# #
# a = {"name":"a"}
# hello = BaseRpc('localhost:50051', 'hello', path='hello2')
# r = hello.send('SayHello', a)
# print(r)