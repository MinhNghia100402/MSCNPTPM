from flask import Flask, request,jsonify
from flask_cors import CORS
import base64
from PIL import Image
import numpy  as np
import argparse
import cv2
import io

from functions import check_face, add_new_face, reload

parser = argparse.ArgumentParser(description='Choose option')
parser.add_argument('-p', '--port', type=int, default=8000)
parser.add_argument('-ht', '--host', type=str, default="0.0.0.0")
args = parser.parse_args()

app = Flask(__name__)
CORS(app)

def load_image2array(data):
    return np.array(Image.open(data))


#================================================================
def base64_to_numpy(base64_string):
    # Lấy chuỗi base64 phần sau dấu phẩy (phần dữ liệu hình ảnh thực sự)
    image_data = base64_string.split(',')[1]

    # Giải mã base64 và chuyển thành numpy array
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    return img_np
#================================================================


@app.post('/check')
# def check():
#     img = load_image2array(request.files['img'].stream)
#     print("checking done")
#     id, name = check_face(img)
#     return {'msv': id, 'name': name}

def check():
    # Nhận dữ liệu hình ảnh từ yêu cầu POST dưới dạng chuỗi base64
    image_base64 = request.json.get('imageSrc')

    # Chuyển dữ liệu base64 thành mảng numpy
    img = base64_to_numpy(image_base64)

    # Tiếp tục xử lý hình ảnh như trước
    print("checking done")
    name,id,lop,year= check_face(img)

    data = {
        "status" : "200",
        "id" : id,
        "name" : name,
        "lop" : lop,
        "year" : year
    }
    print(data)
    return jsonify(data)

# @app.post('/addnew')
# def addNewFace():
#     try:
#         code = request.form['code']
#         name = request.form['name']
#         img = load_image2array(request.files['imgz'].stream)
#         add_new_face(code, name, img)

#         return {'mess': 'success'}
#     except:
#         return {'mess': 'fail'}

@app.post('/addnew')
def addNewFace():
    try:
        code = request.form['id']
        name = request.form['name']
        lop = request.form['class']
        years = request.form['year']

        # Nhận dữ liệu ảnh từ yêu cầu POST
        image_base64 = request.form.get('image')

        if image_base64 is None:
            return {'error': 'No image data received'}

        # Chuyển dữ liệu base64 thành mảng bytes
        image_bytes = base64.b64decode(image_base64.split(',')[1])

        # Chuyển mảng bytes thành đối tượng hình ảnh    
        image = Image.open(io.BytesIO(image_bytes))

        # Chuyển hình ảnh thành mảng NumPy
        img = np.array(image)
        add_new_face(code,name,lop,years,img)

        return {'mess': 'success'}
    except:
        return {'mess':'fail'}

@app.post('/reload')
def reloadData():
    try:
        reload()
        return {'mess': 'success'}
    except:
        return {'mess': 'fail'}

if __name__ == '__main__':
    port = args.port
    host = args.host
    app.run(host=host, port=port, debug=True)