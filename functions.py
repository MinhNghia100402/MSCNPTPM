import cv2
import numpy as np
from model.face import RetinaFace, ArcFace, Landmark
from model.tracking import BYTETracker

retina_face = RetinaFace(model_name='retina_s')
arc_face = ArcFace(model_name='arcface_s')
tracker = BYTETracker()
landmark = Landmark()

# init dataset
import os

recog_data={}
database_emb = {
    'userID': [],
    'embs': []
}

msvs={'ids': []}
data = 'data'
img_data_list = os.listdir(data)
for i in range(len(img_data_list)):
    img_path = os.path.join(data, img_data_list[i])
    img = cv2.imread(img_path)
    fbox, kpss = retina_face.detect(img)
    tbox, tids = tracker.predict(img, fbox)
    # print(kpss[0])
    emb = arc_face.get(img, kpss[0])
    
    database_emb['embs'].append(emb)
    database_emb['userID'].append(img_data_list[i])
print('Extract feature on databse done!')
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

def dectect_tracking_face(img, num_face=None):
    fboxes, _ = retina_face.detect(img)
    if num_face is None:
        num_face = fboxes.shape[0]
    tboxes, tids = tracker.predict(img, fboxes[:num_face])
    tkpss = [None]*len(fboxes)

    # for i, val in enumerate(tboxes):
    #     d = np.sum(np.abs(val-fboxes[:, :-1]), axis=1)
    #     tkpss[i] = fkpss[np.argmin(d)] 

    # test start
    for i in range(len(tboxes)):
            min_d = 9e5
            tb = tboxes[i]
            for j in range(len(fboxes)):
                fb = fboxes[j]
                d = abs(tb[0]-fb[0])+abs(tb[1]-fb[1]) + \
                    abs(tb[2]-fb[2])+abs(tb[3]-fb[3])
                if d < min_d:
                    min_d = d
                    tkpss[i] = kpss[j]
    # test end

    return tids, tboxes, tkpss

def draw_face_box(frame, boxes=None):
    img = frame.copy()
    if boxes is None:
        _, boxes, _ = dectect_tracking_face(img)
    for tbox in boxes:
        box = tbox[:4].astype(int)
        draw_fancy_box(img, (box[0], box[1]), (box[2], box[3]), (127, 255, 255), 2, 10, 20)
    return img

def check_angle_emb(frame, tids, tboxes , tkpss, thread=15):
    ids = []
    embs = []
    for tid, tbox, tkps in zip(tids, tboxes, tkpss):
        land = landmark.get(frame, tbox)
        angle = landmark.get_face_angle(frame, land, False)[1]
        if angle < thread:
            emb = arc_face.get(frame, tkps)
            embs.append(emb)
            ids.append(tid)
    return ids, embs

def find_face_from_database(emb, thresh=0.1):
    dis = np.dot(database_emb['embs'], emb) / (np.linalg.norm(database_emb['embs']) * np.linalg.norm(emb))
    if np.max(dis) > thresh:
        idx = np.argmax(dis)
        return database_emb['userID'][idx]
    else:
        return None

def check_face(img):
    tids, tboxes, tkpss = dectect_tracking_face(img, num_face=1)
    _, embs = check_angle_emb(img, tids, tboxes, tkpss)
    for emb in embs:
        id = find_face_from_database(emb)
        return id
    return None

if __name__ == '__main__':
    img = cv2.imread('./data/test.jpg')
    print(check_face(img))
    print(check_face(img))

    # img = draw_face_box(img)
    

    # print(len(tboxes))
    # tids, tboxes, tkpss = dectect_tracking_face(img, num_face=1)
    

    # img = draw_face_box(img, tboxes)

    # cv2.imwrite('./data/generate.jpg', img)

    # import ipdb; ipdb.set_trace()

    # cap = cv2.VideoCapture(0)
    # while True:
    #     _, frame = cap.read()
    #     frame = cv2.flip(frame, 1)

    #     print(check_face(frame))

    #     cv2.imshow('', frame)

    #     if cv2.waitKey(1) & 0xFF == ord('x'):
    #         # cv2.imwrite('./data/test.jpg', frame)
    #         break
    # cap.release()
    # cv2.destroyAllWindows()