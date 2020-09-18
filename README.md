# grpc测试工具

一共两个方式
1. 纯python，把python代码对grpc的处理用字符串进行拼接，然后转为可执行代码（base）
2. python+go，使用python做为testcase层，go项目[grpcox](https://github.com/gusaul/grpcox)作为grpc请求的解释层


## 项目使用到的开源工具

grpcox服务，[grpcox](https://github.com/gusaul/grpcox)


## 使用方式

1. 到server目录下启动待测rpc服务
```shell
python3 greeter_server.py
```

2. 本地先启动一个grpcox服务,
```shell
go run grpcox.go web`
```

### base

1. 到testcase目录下运行测试用例，
```shell
pytest test_base_demo.py
```


### grpcox

1. 到testcase目录下运行测试用例，
```shell
pytest test_grpcox_demo.py
```