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

from util.base import BaseRpc

class TestHello(object):

    @pytest.fixture(params=[{
        "name": "1",
        "@Req.request_height": { 
            "height":"86"
        }
    }])
    def message(self, request):
        return request.param

    def test_hello(self, message):
        hello = BaseRpc('0.0.0.0:50052', 'hello.hello_app')
        r = hello.send('SayHello', message)
        assert(r.message == 'Hello, 1!')
