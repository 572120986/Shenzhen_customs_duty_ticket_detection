# coding:utf-8

from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from werkzeug.utils import secure_filename
import os
import cv2
import time
from datetime import datetime
from application.invoice_h import invoice_h
from model_postM_invoice import ocr as ocr_M
from datetime import timedelta
import pytz


from text.keras_yolo3 import yolo_text,box_layer,K
#获取keras已经建立的session：
sess = K.get_session()
# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


app = Flask(__name__)
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)

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
# @app.route('/upload', methods=['POST', 'GET'])
@app.route('/upload', methods=['POST', 'GET'])  # 添加路由
def upload():

    if request.method == 'POST':
        print("start", time.asctime(time.localtime(time.time())))
        f = request.files['file']

        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})

        user_input = request.form.get("name")
        invoice_file_name = secure_filename(f.filename)
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(basepath, 'static/images', secure_filename(f.filename))  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径

        f.save(upload_path)

        # 使用Opencv转换一下图片格式和名称
        img = cv2.imread(upload_path)
        cv2.imwrite(os.path.join(basepath, 'static/images',  secure_filename(f.filename)), img)
        result2 = ocr_M(img)
        res = invoice_h(result2)
        res = res.res
        print(str(result2))
        print(str(res))

        tz = pytz.timezone('Asia/Shanghai')  # 东八区
        ocr_identify_time = datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime(
            '%Y-%m-%d %H:%M:%S')
        build_api_result(100, "识别成功", res, invoice_file_name, ocr_identify_time)
        print("over",time.asctime(time.localtime(time.time())))
        return render_template('upload_ok.html', userinput=secure_filename(f.filename), val1=time.time(),build_api_result=res)

    return render_template('upload.html')


if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=8987, debug=True)