from fastapi import FastAPI, UploadFile, File
from PIL import Image
from io import BytesIO
import numpy  as np
import uvicorn
import argparse

from functions import check_face

parser = argparse.ArgumentParser(description='Chooose option')
parser.add_argument('-p', '--port', type=int, default=8000)
parser.add_argument('-ht', '--host', type=str, default="0.0.0.0")
args = parser.parse_args()

app = FastAPI()

def load_image2array(data):
    return np.array(Image.open(BytesIO(data)))

@app.post('/check')
async def check(file: UploadFile = File(...)): 
    img = load_image2array(await file.read())
    id = check_face(img)
    return {'msv': id}

if __name__ == "__main__":
    port = args.port
    host = args.host
    uvicorn.run(app, host=host, port=port)