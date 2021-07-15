import dash
import dash_core_components as dcc
import dash_html_components as html
from picamera.array import PiRGBArray, raw_resolution
from picamera import PiCamera, camera
from flask import Flask, Response
import cv2
import time
import imutils
from pyimagesearch.shapedetector import ShapeDetector

class VideoCamera(object):
    def __init__(self):
        #self.video = cv2.VideoCapture(0) # can do it through OpenCV or picamera
        # Picamera is a little quicker
        # This example is set up to capture full resolution frames on mode 2 (max 15fps)
        self.camera = PiCamera(sensor_mode=2)
        w = 1024 #2592 #640 #1920
        h = 768 #1944 #480 #1080
        self.camera.resolution = (w,h)
        self.camera.framerate = 25 # 32
        self.rawCapture = PiRGBArray(self.camera, size=(w,h))
        time.sleep(0.5)

    def __del__(self):
        #self.video.release() #close the cv2 camera
        self.camera.close()

    def get_frame(self):
        #success, image = self.video.read()
        #ret, jpeg = cv2.imencode('.jpg', image)
        #return jpeg.tobytes()
        frame = self.camera.capture(self.rawCapture, format="bgr", use_video_port=True)
        image = self.rawCapture.array # this is a numpy array : do with it what you will.
        #EG you could get the size of the array:
        #print('img {}x{}'.format(image.shape[1],image.shape[0]))
        image = cv2.resize(image,(1024,768))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        cnts = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        sd = ShapeDetector()
        # loop over the contours
        for c in cnts:
            #filter out contours that are too small/big
            if cv2.contourArea(c) > 1000 and cv2.contourArea(c) < 100000:
                # compute the center of the contour
                M = cv2.moments(c)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                shape = sd.detect(c)
                if shape == "rectangle" or shape == "square":
                    # draw the contour and center of the shape on the image
                    cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                    cv2.circle(image, (cX, cY), 7, (255, 255, 255), -1)
                    
        #once you are ready, convert the frame to a jpg image
        ret, jpeg = cv2.imencode('.jpg', image)
        self.rawCapture.truncate(0) #clear the camera buffer for the next frame
        return jpeg.tobytes()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

@server.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

app.layout = html.Div([
    html.H1("Webcam Test"),
    html.Img(src="/video_feed")
])

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=8050)
