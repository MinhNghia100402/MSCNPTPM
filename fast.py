from fastapi import FastAPI, UploadFile, File
from PIL import Image
from io import BytesIO
import numpy  as np

from functions import check_face

app = FastAPI()

def load_image2array(data):
    return np.array(Image.open(BytesIO(data)))

@app.post('/check')
async def check(file: UploadFile = File(...)): 
    img = load_image2array(await file.read())
    id = check_face(img)
    return {'msv': id}