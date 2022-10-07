from flask import Flask, request
from PIL import Image
import numpy  as np
import argparse

from functions import check_face

parser = argparse.ArgumentParser(description='Chooose option')
parser.add_argument('-p', '--port', type=str, default="8000")
parser.add_argument('-ht', '--host', type=str, default="0.0.0.0")
args = parser.parse_args()

app = Flask(__name__)

def load_image2array(data):
    return np.array(Image.open(data))

@app.post('/check')
def check(): 
    img = load_image2array(request.files['file'].stream)
    id = check_face(img)
    return {'msv': id}

if __name__ == '__main__':
    port = args.port
    host = args.host
    app.run(host=host, port=port, debug=True)