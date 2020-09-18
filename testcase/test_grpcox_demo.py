from __future__ import print_function
import logging
import pytest
import grpc
import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
sys.path.append(curPath)

from util.grpcox import BaseRpc

class TestHello(object):

    @pytest.fixture(params=[{
        "name": "1",
        "requestHeight": {
            "height": "1"
        }
    }])
    def message(self, request):
        return request.param

    def test_hello(self, message):
        hello = BaseRpc('0.0.0.0:50052', rootPath+'/pb2/hello')
        r = hello.send('hello.Greeter','SayHello',message)
        assert(r.strip() == '{\n  \"message\": \"Hello, 1!\"\n}')
