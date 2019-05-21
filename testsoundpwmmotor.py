from matplotlib.mlab import find
import pyaudio
import numpy as np

import RPi.GPIO as GPIO#motor

import pygame
import time

import math
import matplotlib.pyplot as plt
from detect_peaks import detect_peaks
from threading import Thread

#서버에서 받은 sound 사용 
import os
import sys
import requests

#motor
#m1_pin=20
#m2_pin=21
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(m1_pin,GPIO.OUT)
#GPIO.setup(m2_pin,GPIO.OUT)
#GPIO.output(m2_pin,0)
#pw=GPIO.PWM(m1_pin,500)
#duty=0
#pw.start(0)

MinDetect = 50
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "babycry.wav"

p = pyaudio.PyAudio()

babyDidCry = False
endFrame = 0

ffs=[0]
amp=[0]

#서버에서 받은 명령어 실행
ctlurl = 'http://223.194.134.212:80/sound/' #서버 주소 
data = requests.get(ctlurl)


pygame.mixer.init()
pygame.mixer.music.load(data)//값 넣어줌.


def Pitch(signal):
    signal = np.fromstring(signal, 'Int16')
    maXabs = sum(abs(i) for i in signal)/float(len(signal))
    if maXabs >MinDetect:
        crossing = [math.copysign(1.0, s) for s in signal]
        index = find(np.diff(crossing));
        f0=round(len(index) *RATE /(2*np.prod(len(signal))))
        return f0, maXabs;
    else:
        return 0,0


def detecting():
    global babyDidCry
    
    stream = p.open(format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    output = True,
    frames_per_buffer = chunk)

    average = []
    for i in range(0, 5000):
        data = stream.read(chunk, exception_on_overflow = False)
        Frequency, amplitude = Pitch(data)

        ffs.append(Frequency)
        amp.append(amplitude)
        
        
        if (i+1)% 100 == 0:
            avgPeak = []
            if np.count_nonzero(ffs[i-99:])!=0:
                peaks = detect_peaks(ffs[i-99:], mph=1500, mpd=3,show = False)
                averageAmp = np.average(amp[i-99:])
                if len(peaks) >0:
                    for j in peaks:
                        avgPeak.append(ffs[i-99])
                    avgPeakResult = np.average(avgPeak)
                    stdPeak = np.std(avgPeak)
                else:
                    avgPeakResult = 0
                    stdPeak = 0
                print ( avgPeakResult, stdPeak,averageAmp, len(peaks))
                if np.average(avgPeak) <= 2500 and np.std(avgPeak) <200 and averageAmp >30 and len(peaks)>=2 and len(peaks) <14:
                  #  if babyDidCry == False:
                  #      babyDidCry = True
                    endFrame = i + 1500
                    print ("baby crying")                                                                                                                                                                                                                                
                    #pw.ChangeDutyCycle(20)
                    pygame.mixer.music.play()
                    time.sleep(5)
                    #duty=20
                
                else:
                    print ("noise")
                    pygame.mixer.music.stop()
                   #pw.ChangeDutyCycle(0)
            else:
                print ("noise")
                pygame.mixer.music.stop()
                #pw.ChangeDutyCycle(0)
  
detecting()
   
