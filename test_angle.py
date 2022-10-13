import cv2
import numpy as np
import time
from model.face import RetinaFace, ArcFace, Landmark
from model.tracking import BYTETracker
from collections import defaultdict 
import threading
import argparse
import math

parser = argparse.ArgumentParser(description='The smooth demo of webcam of 3DDFA_V2')
parser.add_argument('-f', '--focal_lenght', type=float, default=4)
parser.add_argument('-s', '--sensor_width', type=float, default=3)

args = parser.parse_args()

def def_value(): 
    return "_"

# app = Flask(__name__)
retina_face = RetinaFace(model_name='retina_m')
arc_face = ArcFace(model_name='arcface_m')
bt = BYTETracker()
landmark = Landmark()
gamma = 37.7952755906

recog_data = {
    'time':[],
    'userID':[],
    'emb':[],
    'trackID':[],
    'count_time':[]
}

track_name = defaultdict(def_value) 
track_emb = {}
current_tracking = {}
name_idx = 0

def recog():
    global track_emb, track_name, recog_data, current_tracking
    
    cap = cv2.VideoCapture(0)
    ret, _ = cap.read()

    t = time.time()
    while ret:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        fboxes,kpss = retina_face.detect(frame)
        
        tboxes, tids = bt.predict(frame, fboxes)

        tkpss = [None]*len(fboxes)
        for i in range(len(tboxes)):
            min_d = 9e5
            tb = tboxes[i]
            for j in range(len(fboxes)):
                fb = fboxes[j]
                d = abs(tb[0]-fb[0])+abs(tb[1]-fb[1])+abs(tb[2]-fb[2])+abs(tb[3]-fb[3])
                if d < min_d:
                    min_d = d
                    tkpss[i] = kpss[j]

        embs = []
        ids = []
        for tid, tbox, tkps in zip(tids, tboxes, tkpss):
            box = tbox[:4].astype(int)
            if tid in recog_data['trackID']:
                idx = recog_data['trackID'].index(tid)
                recog_data['time'][idx] = time.time()
            else:
                land = landmark.get(frame, tbox)
                angle = landmark.get_face_angle(frame, land, False)[1]
                            
                if abs(angle) < 15:
                    emb = arc_face.get(frame, tkps)
                    embs.append(emb)
                    ids.append(tid)
        current_tracking = {'frame':frame.copy(), 'track_id': ids, 'embs':embs}

        for box, tid in zip(tboxes,tids):
                # print(box)
            box = box[:4].astype(int)

            land = landmark.get(frame, box)
            pointLeft = land[88].astype(int)
            pointRight = land[38].astype(int)
            point_noise = land[86].astype(int)
            x_point_noise = point_noise[0]
            st = str(tid)
            
            if tid in recog_data['trackID']:
                st = recog_data['userID'][recog_data['trackID'].index(tid)]
                
            view, d_pixel,d = just_look_only_display(land, frame, tid, pointLeft, pointRight, x_point_noise)
            
            
            cv2.putText(frame, st, (box[0], box[1]-40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)
            draw_fancy_box(frame, (box[0],box[1]), (box[2],box[3]), (127, 255, 255), 2, 10, 20)

            updown = landmark.get_face_angle(frame, land, False)
            look = get_look(updown[0])
            if view == 1:
            # if view == 1 and look !="OUT":

                cv2.putText(frame,f'line_view:{view}' , (box[0], box[1]-10) , cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)
                if tid in recog_data['trackID']:
                    idx = recog_data['trackID'].index(tid)
                    recog_data['count_time'][idx] += time.time()-t
                    t = time.time()
                    
                    angle_retina = updown[1]
            else:
                t = time.time()
                cv2.putText(frame,f'line_view:None' , (box[0], box[1]-10) , cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0,255), 2)
            
        for i in range(len(recog_data['userID'])):                
            cv2.putText(frame, '{}: {:0.3f}'.format(recog_data['userID'][i], recog_data['count_time'][i]), (10, 20+i*25), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,0), 2  )

        cv2.imshow('qwe', frame)
        if cv2.waitKey(1) & 0xFF == ord('x'):
            break
    cap.release()
    cv2.destroyAllWindows()

def get_look(angle):
    if angle < -160 and angle >=-165:
        head = "down"
    elif angle >-170 and angle <-165: head = "straight"
    elif angle<-170 and angle > -175 : head = "up"
    else: head = "OUT"
    return head

def get_leftright(angle, monitor):
    if monitor == 1:
        if int(angle) <= 0: 
            head = "Left"
        elif (int(angle)  > 0 ) and (int(angle) < 11): 
            head = "Middle"
        elif (int(angle)  >= 11 ): 
            head = "Right"
            
    elif monitor == 0:
        if int(angle) < -4:
            head = "Left"
        elif ( int(angle) >=-4 ) and ( int(angle) <=4):
            head = "Middle"
        elif (int(angle) > 4):
            head = "Right"
            
    elif monitor == -1:        
        if int(angle) >= 0: 
            head = "Right"
        elif (int(angle)  < 0 ) and (int(angle) > -11): 
            head = "Middle"
        elif (int(angle)  <= -11 ): 
            head = "Left"
            
    return head
def cal_distance(w, focal_lenght,frame,sensor_width):
    W = 6.3 #distance between two eyes in real life
    d = ((W*focal_lenght*frame.shape[0])/((w+1e-10)*sensor_width))
    return d

def get_monitor(x_point_noise, length_monitor):
    """_summary_
    Args:
        length_monitor(int): length of monitor
    Returns:
        monitor: monitor
    """
    if x_point_noise < length_monitor / 3:
        monitor = -1
    elif x_point_noise < length_monitor * 2/3:
        monitor = 0
    else:
        monitor = 1
    return monitor

def rule_angle(angle_retina, x_point_noise, distance_pixel, lenght_monitor, bias):
    line_view = None
    monitor = get_monitor(x_point_noise, lenght_monitor)
    print(monitor)
    alpha_lim_left = math.atan(x_point_noise/distance_pixel) * 180 / math.pi
    print(distance_pixel)
    print('alpha_lim_left: ',alpha_lim_left)
    alpha_lim_right = math.atan((lenght_monitor-x_point_noise)/distance_pixel) * 180 / math.pi
    print('alpha_lim_right: ',alpha_lim_right)
    print('sangle-retina: ', angle_retina)
    print('------------------------')   
    if monitor == -1:
        # print('aaaaaaaaaaaaaaaaaaaaaaaaa')
        if (angle_retina < 0) and (abs(angle_retina) < alpha_lim_left + bias):
            line_view = -1
        if (angle_retina > 0) and (angle_retina < alpha_lim_right + bias):
            projection = distance_pixel*math.tan(angle_retina) 
            line_view = get_monitor(projection + x_point_noise, lenght_monitor)
            
    elif monitor == 1:
        # print('bbbbbbbbbbbbbbbbbb')
        if (angle_retina < 0) and (abs(angle_retina) < alpha_lim_left + bias):
            projection = distance_pixel*math.tan(angle_retina)
            line_view = get_monitor(x_point_noise - projection, lenght_monitor)
        if (angle_retina > 0) and (angle_retina < alpha_lim_right):
            line_view = 1
            
    elif monitor == 0:
        # print('cccccccccccccccccc')
        if (angle_retina < 0) and (abs(angle_retina) < alpha_lim_left + bias):
            if x_point_noise - distance_pixel*math.tan(angle_retina) < lenght_monitor/3:
                line_view=-1
            elif x_point_noise - distance_pixel*math.tan(angle_retina) < (2*lenght_monitor)/3:
                line_view=0
        if (angle_retina > 0) and (abs(angle_retina) < alpha_lim_right + bias):
            if x_point_noise + distance_pixel*math.tan(angle_retina) < (2*lenght_monitor)/3:
                line_view = 0
            elif x_point_noise + distance_pixel*math.tan(angle_retina) > (2*lenght_monitor)/3:
                line_view = 1
    if line_view == -1:
        line_view = "Left"
    elif line_view == 0:
        line_view = 'Middle'
    elif line_view == 1:
        line_view = 'Right'
    return line_view

def new_rule_angle(angle_retina, x_point_noise, distance_pixel, lenght_monitor, bias):
    line_view = None
    alpha_lim_left = math.atan(x_point_noise/distance_pixel) * 180 / math.pi
    # print(distance_pixel)
    # print('alpha_lim_left: ',alpha_lim_left)
    
    alpha_lim_right = math.atan((lenght_monitor-x_point_noise)/distance_pixel) * 180 / math.pi
    # print('alpha_lim_right: ',alpha_lim_right)
    # print('angle-retina: ', angle_retina)
    # print('------------------------')
    
    if (angle_retina < 0 ) and (abs(angle_retina) < alpha_lim_left + bias):
        line_view = 1
    if (angle_retina > 0) and (angle_retina < alpha_lim_right + bias):
        line_view = 1
    return line_view
      
def just_look_only_display(land, frame, ids, pointLeft, pointRight, x_point_noise):
    """_summary_
    Args:
        land (_type_): land = landmark.get(frame, box)
        frame (_type_): frame
        ids (_type_): id tracing
    Returns:
        view: line view
    """

    # cv2.circle(frame, pointLeft,5,(0,255,0),cv2.FILLED)
    # cv2.circle(frame, pointRight,5,(0,255,0),cv2.FILLED)
    # cv2.circle(frame, point_noise,5,(0,255,0),cv2.FILLED)
    dx2 = (pointLeft[0]-pointRight[0])**2          
    dy2 = (pointLeft[1]-pointRight[1])**2   
    w = math.sqrt(dx2 + dy2)
    angle = landmark.get_face_angle2(frame, land)
    phi = 90-abs(angle)
    W = 6.3
    # f = 1190
    f = args.focal_lenght
    w = w/(math.sin(phi*math.pi/180)) 
    d = cal_distance(w, f, frame, args.sensor_width)
    # cv2.putText(frame,f'Angle:{int(angle)}' , land[30].astype(int) , cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)
    # cv2.putText(frame,f'ID:{int(ids)}' , land[25].astype(int) , cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)              
    d_pixel = d * gamma
    view = new_rule_angle(angle_retina=angle, x_point_noise=x_point_noise, distance_pixel=d_pixel, lenght_monitor=frame.shape[1], bias=0)
    return view, d_pixel,d


def check_emb_in_data():
    global track_emb, recog_data, track_name, current_tracking, name_idx
    while True:
        # print(len(recog_data['emb']), len(recog_data['time']), len(recog_data['trackID']),len(recog_data['userID']))
        if 'track_id' not in current_tracking.keys():
            time.sleep(1)
            continue
        time.sleep(0.1)     
        for idt, emb in zip(current_tracking['track_id'], current_tracking['embs']): #track_emb.items():
            if len(recog_data['emb'])==0:
                print('check2')
                recog_data['time'].append(time.time())
                recog_data['userID'].append('user_{:d}'.format(name_idx))
                name_idx += 1
                recog_data['emb'].append(emb)
                recog_data['trackID'].append(idt)
                recog_data['count_time'].append(0)
            else:
                # print('check3')
                distance = np.linalg.norm(recog_data['emb'] - emb, axis=1)
                
                if min(distance) < 21:
                    idx = np.argmin(distance)
                    name = recog_data['userID'][idx]
                    recog_data['time'][idx] = time.time()
                    recog_data['emb'][idx] = emb
                    recog_data['trackID'][idx] = idt
                else:
                    recog_data['time'].append(time.time())
                    recog_data['userID'].append('user_{:d}'.format(name_idx))
                    name_idx += 1
                    recog_data['emb'].append(emb)
                    recog_data['trackID'].append(idt)
                    recog_data['count_time'].append(0)
                    

def remove_10s():
    global recog_data, track_emb, track_name, current_tracking
    while True:
        t_rm = time.time()
        for i in range(len(recog_data['userID'])):
            if (t_rm - recog_data['time'][i]) >10:
                # tid = recog_data['trackID'][i]
                del recog_data['emb'][i]
                del recog_data['userID'][i]
                del recog_data['time'][i]
                del recog_data['trackID'][i]
                del recog_data['count_time'][i]
                break

                # del track_emb[tid]
                # del track_name[tid]
        time.sleep(0.5)
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
# @app.route('/')

# def video_feed():
#     #Video streaming route. Put this in the src attribute of an img tag
#     return Response(recog(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    threading.Thread(target=remove_10s, args=()).start()
    threading.Thread(target=check_emb_in_data, args=()).start()
    recog()