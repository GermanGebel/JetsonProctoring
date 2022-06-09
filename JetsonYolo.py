import cv2
import numpy as np
from elements.yolo import OBJ_DETECTION, OBJ_DETECTION_TRT
import time
from Proctoring import Proctoring

Object_classes = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
                'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
                'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
                'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
                'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
                'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
                'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
                'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
                'hair drier', 'toothbrush']

Object_colors = list(np.random.rand(80,3)*255)
Object_detector = OBJ_DETECTION('weights/yolov5s.pt', Object_classes)

PROCTORING_CLASSES = ['person', 'cell phone']

def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

def error_to_image(img, msg):
    return cv2.putText(img, f'{msg}', img.size() // 2, cv2.FONT_HERSHEY_SIMPLEX , 0.75, color, 1, cv2.LINE_AA)

# To flip the image, modify the flip_method parameter (0 and 2 are the most common)
print(gstreamer_pipeline(flip_method=0))
cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
if cap.isOpened():
    window_handle = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
    # Window
    # --------------------- TIMER ---------------------
    proctor = Proctoring(checking_time=5)

    while cv2.getWindowProperty("CSI Camera", 0) >= 0:
        # PROCTOR CHECK TIME
        proctor.check_time()

        ret, frame = cap.read()
        frame = cv2.flip(frame,-1)
        # original = frame.copy()
        if ret:
            # detection process
            objs = Object_detector.detect(frame)

            people = 0
            smartphones = 0

            # plotting
            for obj in objs:
                if obj['label'] in PROCTORING_CLASSES:
                    highlight_object_flag = False
                    # print(obj)
                    label = obj['label']
                    score = obj['score']
                    # counts
                    if label == 'person' and score > 0.6:
                        people += 1
                        highlight_object_flag = True
                        
                    if label == 'cell phone' and score > 0.6:
                        smartphones += 1
                        highlight_object_flag = True
                    
                    if highlight_object_flag:
                        [(xmin,ymin),(xmax,ymax)] = obj['bbox']
                        color = Object_colors[Object_classes.index(label)]
                        frame = cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), color, 2) 
                        frame = cv2.putText(frame, f'{label} ({str(score)})', (xmin,ymin), cv2.FONT_HERSHEY_SIMPLEX , 0.75, color, 1, cv2.LINE_AA)
            
            frame = proctor.work_with_frame(frame)
            proctor.people_per_frame.append(people)
            proctor.smartphones_per_frame.append(smartphones)

	    # if frame.size()[0] > 0 and frame.size()[1] > 0:
        cv2.imshow("CSI Camera", frame)
        if proctor.game_over:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            frame = cv2.putText(frame, 'GAME OVER', (0, 400), cv2.FONT_HERSHEY_SIMPLEX , 2, color, 3, cv2.LINE_AA)
            start = time.time()
            while time.time() - start < 5:
                cv2.imshow("CSI Camera", frame)
            # time.sleep(5)
            break
        keyCode = cv2.waitKey(30)
        if keyCode == ord('q'):
            break
    cv2.imshow("CSI Camera", frame)
    # time.sleep(5)
    cap.release()
    cv2.destroyAllWindows()
else:
    print("Unable to open camera")
