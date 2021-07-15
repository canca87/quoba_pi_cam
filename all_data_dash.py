import dash
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
import flask
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import os
import numpy as np
from flask import Flask,Response
from picamera.array import PiRGBArray, raw_resolution
from picamera import PiCamera, camera
import time
import cv2
from devices.gps_device import gps_device
from devices.us_distance_device import us_distance_device
from devices.lidar_distance_device import lidar_distance_device
from devices.imu_device import imu_device
from devices.pi_device import pi_device

# Setup the subsystems
gps_sys = gps_device()
us_distance_sys = us_distance_device()
lidar_distance_sys = lidar_distance_device()
imu_sys = imu_device()
pi_sys = pi_device()

class VideoCamera(object):
    def __init__(self):
        self.camera = PiCamera()
        w = 640#1024
        h = 480#768
        self.camera.resolution = (w,h)
        self.camera.framerate = 25 # 32
        self.rawCapture = PiRGBArray(self.camera, size=(w,h))
        time.sleep(0.5)

    def __del__(self):
        self.camera.close()

    def get_frame(self):
        frame = self.camera.capture(self.rawCapture, format="bgr", use_video_port=True)
        image = self.rawCapture.array # this is a numpy array : do with it what you will.
        #EG you could get the size of the array:
        #print('img {}x{}'.format(image.shape[1],image.shape[0]))

        #once you are ready, convert the frame to a jpg image
        ret, jpeg = cv2.imencode('.jpg', image)
        self.rawCapture.truncate(0) #clear the camera buffer for the next frame
        return jpeg.tobytes()

def gen_html_image_frame(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Example data (a circle).
#resolution = 200
#X = range(-resolution,0,1)
#Y = deque(maxlen = resolution)
#Y.append(get_cpu_temp())
#t = np.linspace(0, np.pi * 2, resolution)
#x, y = np.cos(t), np.sin(t)
# Example app.
figure = dict(data=[{'x': [], 'y': []}], layout=dict(xaxis=dict(range=[-10, 100]), yaxis=dict(range=[0,60])))
server = Flask(__name__)
app = dash.Dash(__name__, server=server, update_title=None)  # remove "Updating..." from title
app.layout = html.Div([html.Img(src="/video_feed"),
    html.Div(id='textarea-output', style={'whiteSpace': 'pre-line'}),
    #dcc.Graph(id='graph', figure=figure), 
    dcc.Interval(id="interval",interval = 1000,)
    ])

@server.route('/video_feed')
def video_feed():
    return Response(gen_html_image_frame(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.callback(Output('graph', 'prependData'), 
    [Input('interval', 'n_intervals'),State('graph', 'figure')])
def update_data(n_intervals,this_fig):
    #index = n_intervals % resolution
    #Y.append(get_gpu_temp())
    #print(len(list(range(0,len(Y)))))
    #print(len(list(Y)))
    #print(list(range(0,len(Y)))[-1])
    #print(list(Y)[-1])
    # tuple is (dict of new data, target trace index, number of points to keep)
    #return dict(x=[[x[index]]], y=[[y[index]]]), [0], 100
    return dict(x=[[0]],y=[[1]]), [0], 100

@app.callback(
    Output('textarea-output', 'children'),
    Input('interval', 'n_intervals')
)
def update_output(n_intervals):
    msg = 'GPS data\n\r############################\n\r{}'.format(gps_sys.getText())
    msg = "{}\n\r\n\rUltrasonic distance sensor data\n\r############################\n\r{}".format(msg,us_distance_sys.getText())
    msg = "{}\n\r\n\rLidar distance sensor data\n\r############################\n\r{}".format(msg,lidar_distance_sys.getText())
    msg = "{}\n\r\n\rIMU sensor data\n\r############################\n\r{}".format(msg,imu_sys.getText())
    msg = "{}\n\r\n\rMCU data\n\r############################\n\r{}".format(msg,pi_sys.getText())
    return msg

if __name__ == '__main__':
    app.run_server(host='0.0.0.0',port=8014)