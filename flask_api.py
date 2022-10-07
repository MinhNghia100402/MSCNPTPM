from flask import Flask, request
from PIL import Image
import numpy  as np
import cv2

from functions import check_face

app = Flask(__name__)

def load_image2array(data):
    return np.array(Image.open(data))

@app.post('/check')
def check(): 
    img = load_image2array(request.files['file'].stream)
    cv2.imwrite('./data/api_generate.jpg', cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    id = check_face(img)
    return {'msv': id}

if __name__ == '__main__':
    app.run(port='8080', debug=True)