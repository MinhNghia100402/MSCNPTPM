from flask import Flask, request
from flask_cors import CORS

from PIL import Image
import numpy  as np
import argparse

from functions import check_face, add_new_face, reload

parser = argparse.ArgumentParser(description='Choose option')
parser.add_argument('-p', '--port', type=int, default=8000)
parser.add_argument('-ht', '--host', type=str, default="0.0.0.0")
args = parser.parse_args()

app = Flask(__name__)
CORS(app)

def load_image2array(data):
    return np.array(Image.open(data))

@app.post('/check')
def check():
    img = load_image2array(request.files['img'].stream)

    id, name = check_face(img)

    return {'msv': id, 'name': name}

@app.post('/addnew')
def addNewFace():
    try:
        code = request.form['code']
        name = request.form['name']
        img = load_image2array(request.files['img'].stream)

        add_new_face(code, name, img)

        return {'mess': 'success'}
    except:
        return {'mess': 'fail'}

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