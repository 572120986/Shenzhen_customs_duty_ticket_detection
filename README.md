# Shenzhen customs duty ticket
  识别type:深圳海关税票；识别字段为：填发日期、号码、账号、公司名称、合计、类型等
## 环境
   1. python3.6
   2. 依赖项安装：pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple 
   3. 有GPU环境的可修改安装requirements.txt对应版本的tensorflow-gpu，config.py文件中控制GPU的开关
## 模型架构
    YOLOv3 + CRNN + CTC
## 模型
   1. 模型下载地址：私信
   2. 将下载完毕的模型文件夹models放置于项目根目录下
## 服务启动
   1. python3 app.py
   2. 端口可自行修改
   3. 服务调用地址：http://*.*.*.*: [端口号]/models，例：http://127.0.0.1:11111/models
## 测试demo
   1. 测试工具：postman，可自行下载安装
   2. 海关税票测试结果
   
   
   ## 参考
chineseocr https://github.com/chineseocr/chineseocr
