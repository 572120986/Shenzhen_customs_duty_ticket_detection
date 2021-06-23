from flask import Flask, jsonify, request, redirect, render_template
from flask_cors import CORS
import time
import os
import cv2
from datetime import datetime
from application.invoice_h import invoice_h
from model_postM_invoice import ocr as ocr_M
import pytz
import web

basepath = os.path.dirname(__file__)  # 当前文件所在路径
render = web.template.render('templates', base='base')
port = 8804
allowed_extension = ['jpg','png','JPG']
# Flask
app = Flask(__name__)
CORS(app, resources=r'/*')

# 构建接口返回结果
def build_api_result(code, message, data,file_name,ocr_identify_time):
    result = {
        "code": code,
        "message": message,
        "data": data,
        "FileName": file_name,
        "ocrIdentifyTime": ocr_identify_time
    }
    return jsonify(result)

# 检查文件扩展名
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extension


# 海关税票OCR识别接口
@app.route('/models', methods=['POST'])
def invoice_ocr():
    # 校验请求参数
    if 'file' not in request.files:
        return build_api_result(101, "请求参数错误", {},{},{})
    # 获取请求参数
    file = request.files['file']
    invoice_file_name = file.filename
    # 检查文件扩展名
    if not allowed_file(invoice_file_name):
        return build_api_result(102, "失败，文件格式问题", {},{},{})
    upload_path = r"C:\Users\Administrator\Desktop\msdszhong\invoice-master\invoice-master\test"
    whole_path = os.path.join(basepath+'/test',invoice_file_name)
    file.save(whole_path)
    #去章处理方法
    # def remove_stamp(path,invoice_file_name):
    #     img = cv2.imread(path,cv2.IMREAD_COLOR)
    #     # cv2.imshow("noquzhang", img)
    #     B_channel,G_channel,R_channel=cv2.split(img)     # 注意cv2.split()返回通道顺序
    #     _,RedThresh = cv2.threshold(R_channel,170,355,cv2.THRESH_BINARY)
    #     # cv2.imshow("quzhang",RedThresh)
    #     # cv2.waitKey(0)
    #     cv2.imwrite(r'C:\Users\Administrator\Desktop\msdszhong\invoice-master\invoice-master\test/RedThresh_{}.jpg'.format(invoice_file_name),RedThresh)
    #     remove_stamp(path,invoice_file_name)

    # remove_stamp(whole_path, invoice_file_name)
    img1 = cv2.imread(whole_path)
    result2 = ocr_M(img1)
    res = invoice_h(result2)
    res = res.res
    print(str(result2))
    print(str(res))
    tz = pytz.timezone('Asia/Shanghai')  # 东八区
    ocr_identify_time = datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime(
        '%Y-%m-%d %H:%M:%S')
    return build_api_result(100, "识别成功", res, invoice_file_name, ocr_identify_time)


urls = ('/ocr', 'OCR',)
if __name__ == "__main__":
    # Run
    # app = web.application(urls, globals())
    # app.run()
    # app.config['JSON_AS_ASCII'] = False
    # app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    app.run(host='0.0.0.0', port=8804, debug=True)
