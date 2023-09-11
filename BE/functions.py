import os
import cv2
import numpy as np
from model.face import RetinaFace, ArcFace, Landmark
from model.tracking import BYTETracker
import argparse

parser = argparse.ArgumentParser(description='Chooose option')
parser.add_argument('-d', '--dataset', type=str, default="data")
parser.add_argument('-m', '--max_face', type=int, default=-1)
args = parser.parse_args()

retina_face = RetinaFace(model_name='retina_s')
arc_face = ArcFace(model_name='arcface_s')
tracker = BYTETracker()
landmark = Landmark()

def reload():
    global recog_data
    global database_emb

    recog_data={}
    database_emb = {
        'userID': [],
        'embs': []
    }
    try:
        img_data_list = os.listdir(path_data)
        for i in range(len(img_data_list)):
            img_path = os.path.join(path_data, img_data_list[i])
            img = cv2.imread(img_path)
            fbox_data, kpss_data = retina_face.detect(img)
            # kpss: keypoint
            emb_data = arc_face.get(img, kpss_data[0])
            
            database_emb['embs'].append(emb_data)
            database_emb['userID'].append(img_data_list[i].split('.')[-2])
        print('Extract feature on databse done!')
    except:
        print('The database path error!')
    database_emb['embs'] = np.array(database_emb['embs'])

# init dataset
path_data = args.dataset

reload()
# end init dataset

def draw_fancy_box(img, pt1, pt2, color, thickness, r, d):
    x1, y1 = pt1
    x2, y2 = pt2

    # Top left
    cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
    cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)

    # Top right
    cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
    cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)

    # Bottom left
    cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
    cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)

    # Bottom right
    cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
    cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)

def dectect_tracking_face(img, num_face=-1):
    fboxes, kpss = retina_face.detect(img, max_num=num_face)
    tboxes, tids = tracker.predict(img, fboxes)
    tkpss = [None]*len(tboxes)
    for i, val in enumerate(tboxes):
        d = np.sum(np.abs(val-fboxes[:, :-1]), axis=1)
        tkpss[i] = kpss[np.argmin(d)]

    return tids, tboxes, tkpss

def draw_face_box(frame, thread=20, num_face=-1):
    img = frame.copy()
    tids, tboxes, tkpss = dectect_tracking_face(img, num_face=num_face)
    _, embs = check_angle_emb(img, tids, tboxes, tkpss, thread)

    for tbox, emb in zip(tboxes, embs):
        box = tbox[:4].astype(int)
        id = None if emb is None else find_face_from_database(emb)
        cv2.putText(img, ("Strange", id)[id != None], (box[0], box[1]-10), cv2.FONT_HERSHEY_COMPLEX, 1, ((0, 0, 255), (0, 255, 0))[id != None], 2)
        draw_fancy_box(img, (box[0], box[1]), (box[2], box[3]), (127, 255, 255), 2, 10, 20)
    return img

def check_angle_emb(frame, tids, tboxes , tkpss, thread=15):
    ids = []
    embs = []
    for tid, tbox, tkps in zip(tids, tboxes, tkpss):
        land = landmark.get(frame, tbox)
        angle = landmark.get_face_angle(frame, land, False)[1]
        if abs(angle) < thread:
            emb = arc_face.get(frame, tkps)
            embs.append(emb)
            ids.append(tid)
        else:
            embs.append(None)
            ids.append(tid)
    return ids, embs

def find_face_from_database(emb, thresh=0.3):
    if database_emb['embs'].shape[0] == 0:
        return None
    dis = np.dot(database_emb['embs'], emb) / (np.linalg.norm(database_emb['embs'], axis=1) * np.linalg.norm(emb))
    if np.max(dis) > thresh:
        idx = np.argmax(dis)
        return database_emb['userID'][idx]
    else:
        return None

def check_face(img):
    tids, tboxes, tkpss = dectect_tracking_face(img)
    _, embs = check_angle_emb(img, tids, tboxes, tkpss)
    id, name,lop,years = None, None , None , None 
    for emb in embs:
        id = None if emb is None else find_face_from_database(emb)
        if id is not None:
            name, id ,lop,years= id.split('_')
    return name, id,lop,years

def add_new_face(code, name,lop,years ,img):
    _, kpss_data = retina_face.detect(img)
    
    emb_data = arc_face.get(img, kpss_data[0])

    userID = f'{name}_{code}_{lop}_{years}'
    if userID in database_emb['userID']:
        idx = database_emb['userID'].index(userID)
        database_emb['embs'][idx] = emb_data
    else:
        if database_emb['embs'].shape[0] == 0:
            database_emb['embs'] = np.expand_dims(emb_data, axis=0)
        else:
            database_emb['embs'] = np.append(database_emb['embs'], np.expand_dims(emb_data, axis=0), axis=0)
        database_emb['userID'].append(userID)

    img_path = os.path.join(path_data, f'{userID}.jpg')
    cv2.imwrite(img_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

if __name__ == '__main__':
    mx_face = args.max_face
    
    cap = cv2.VideoCapture(0)
    while True:
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)

        img = draw_face_box(frame, 20, mx_face)

        cv2.imshow('', img)

        if cv2.waitKey(1) & 0xFF == ord('x'):
            break
    cap.release()
    cv2.destroyAllWindows()