#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import smbus
import os
import random
import pygame
import threading

#i2c地址
PAJ7620U2_I2C_ADDRESS   = 0x73
#寄存器Bank选择
PAJ_BANK_SELECT         = 0xEF          #Bank0== 0x00,Bank1== 0x01
#寄存器Bank 0
PAJ_SUSPEND             = 0x03      #I2C suspend命令(写= 0x01进入挂起状态)。I2C唤醒命令是奴隶ID唤醒。参考主题“I2C总线定时特性和协议”
PAJ_INT_FLAG1_MASK      = 0x41      #手势检测中断标志掩码
PAJ_INT_FLAG2_MASK      = 0x42      #手势/PS检测中断标志掩码
PAJ_INT_FLAG1           = 0x43      #手势检测中断标志
PAJ_INT_FLAG2           = 0x44      #手势/PS检测中断标志
PAJ_STATE               = 0x45      #手势检测状态指示灯(仅在手势检测模式下起作用)
PAJ_PS_HIGH_THRESHOLD   = 0x69      #PS迟滞高阈值(仅在接近检测模式下起作用)    
PAJ_PS_LOW_THRESHOLD    = 0x6A      #PS迟滞低阈值(仅在接近检测模式下起作用)
PAJ_PS_APPROACH_STATE   = 0x6B      #PS趋近状态，趋近= 1，(8位PS数据>= PS高门限)，不趋近= 0，(8位PS数据<= PS低门限)(仅在接近检测模式下有效)
PAJ_PS_DATA             = 0x6C      #PS 8位数据(仅在手势检测模式下有效)
PAJ_OBJ_BRIGHTNESS      = 0xB0      #物体亮度(最大255)
PAJ_OBJ_SIZE_L          = 0xB1      #对象大小(低8位)   
PAJ_OBJ_SIZE_H          = 0xB2      #对象大小(高8位)   
#寄存器Bank 1
PAJ_PS_GAIN             = 0x44      #PS增益设置(仅在接近检测模式下有效)
PAJ_IDLE_S1_STEP_L      = 0x67      #空闲S1步长，用于设置S1，响应系数(低8位)
PAJ_IDLE_S1_STEP_H      = 0x68      #空闲S1步长，用于设置S1，响应系数(高8位) 
PAJ_IDLE_S2_STEP_L      = 0x69      #空闲S2步长，用于设置S2，响应因子(低8位)
PAJ_IDLE_S2_STEP_H      = 0x6A      #空闲S2步长，用于设置S2，响应因子(高8位)
PAJ_OPTOS1_TIME_L       = 0x6B      #OPtoS1 Step，用于将操作状态的OPtoS1时间设置为待机1状态(低8位)
PAJ_OPTOS2_TIME_H       = 0x6C      #OPtoS1 Step，用于将OPtoS1运行状态时间设置为待机1 stateHigh 8位)  
PAJ_S1TOS2_TIME_L       = 0x6D      #S1toS2步，用于将待机1状态的S1toS2时间设置为待机2状态(低8位)  
PAJ_S1TOS2_TIME_H       = 0x6E      #S1toS2步，用于将待机1状态的S1toS2时间设置为待机2状态高8位) 
PAJ_EN                  = 0x72      #启用/禁用PAJ7620U2
#手势检测中断标志
PAJ_RIGHT               = 0x01 
PAJ_LEFT                = 0x02
PAJ_UP                  = 0x04 
PAJ_DOWN                = 0x08
PAJ_FORWARD             = 0x10 
PAJ_BACKWARD            = 0x20
PAJ_CLOCKWISE           = 0x40
PAJ_COUNT_CLOCKWISE     = 0x80
PAJ_WAVE                = 0x100
#启动初始化阵列
Init_Register_Array = (
    (0xEF,0x00),
    (0x37,0x07),
    (0x38,0x17),
    (0x39,0x06),
    (0x41,0x00),
    (0x42,0x00),
    (0x46,0x2D),
    (0x47,0x0F),
    (0x48,0x3C),
    (0x49,0x00),
    (0x4A,0x1E),
    (0x4C,0x20),
    (0x51,0x10),
    (0x5E,0x10),
    (0x60,0x27),
    (0x80,0x42),
    (0x81,0x44),
    (0x82,0x04),
    (0x8B,0x01),
    (0x90,0x06),
    (0x95,0x0A),
    (0x96,0x0C),
    (0x97,0x05),
    (0x9A,0x14),
    (0x9C,0x3F),
    (0xA5,0x19),
    (0xCC,0x19),
    (0xCD,0x0B),
    (0xCE,0x13),
    (0xCF,0x64),
    (0xD0,0x21),
    (0xEF,0x01),
    (0x02,0x0F),
    (0x03,0x10),
    (0x04,0x02),
    (0x25,0x01),
    (0x27,0x39),
    (0x28,0x7F),
    (0x29,0x08),
    (0x3E,0xFF),
    (0x5E,0x3D),
    (0x65,0x96),
    (0x67,0x97),
    (0x69,0xCD),
    (0x6A,0x01),
    (0x6D,0x2C),
    (0x6E,0x01),
    (0x72,0x01),
    (0x73,0x35),
    (0x74,0x00),
    (0x77,0x01),
)
#寄存器初始化数组
Init_PS_Array = (
    (0xEF,0x00),
    (0x41,0x00),
    (0x42,0x00),
    (0x48,0x3C),
    (0x49,0x00),
    (0x51,0x13),
    (0x83,0x20),
    (0x84,0x20),
    (0x85,0x00),
    (0x86,0x10),
    (0x87,0x00),
    (0x88,0x05),
    (0x89,0x18),
    (0x8A,0x10),
    (0x9f,0xf8),
    (0x69,0x96),
    (0x6A,0x02),
    (0xEF,0x01),
    (0x01,0x1E),
    (0x02,0x0F),
    (0x03,0x10),
    (0x04,0x02),
    (0x41,0x50),
    (0x43,0x34),
    (0x65,0xCE),
    (0x66,0x0B),
    (0x67,0xCE),
    (0x68,0x0B),
    (0x69,0xE9),
    (0x6A,0x05),
    (0x6B,0x50),
    (0x6C,0xC3),
    (0x6D,0x50),
    (0x6E,0xC3),
    (0x74,0x05),
)
#手势寄存器初始化数组
Init_Gesture_Array = (
    (0xEF,0x00),
    (0x41,0x00),
    (0x42,0x00),
    (0xEF,0x00),
    (0x48,0x3C),
    (0x49,0x00),
    (0x51,0x10),
    (0x83,0x20),
    (0x9F,0xF9),
    (0xEF,0x01),
    (0x01,0x1E),
    (0x02,0x0F),
    (0x03,0x10),
    (0x04,0x02),
    (0x41,0x40),
    (0x43,0x30),
    (0x65,0x96),
    (0x66,0x00),
    (0x67,0x97),
    (0x68,0x01),
    (0x69,0xCD),
    (0x6A,0x01),
    (0x6B,0xB0),
    (0x6C,0x04),
    (0x6D,0x2C),
    (0x6E,0x01),
    (0x74,0x00),
    (0xEF,0x00),
    (0x41,0xFF),
    (0x42,0x01),
)

folder = '/home/pi/Desktop/Music/'
playlist = []
randomOrder = False
num = 0
playing = False
volume = 50
nowPlaying = ''

def initPlayer():
    pygame.mixer.init()
    os.system('amixer set Master ' + str(volume) + '%')

def loadPlaylist():
    global playlist
    playlist = []
    files = os.listdir(folder)
    for i in files:
        if i.endswith(('.mp3', '.wav', '.ogg', 'flac')):
            playlist.append(folder + i)

def playMusic():
    global playing
    global nowPlaying
    playing = True
    global num
    if num >= 0 and num < len(playlist):
        while playing:
            if not pygame.mixer.music.get_busy():
                nextMusic = playlist[num]
                nowPlaying = nextMusic
                pygame.mixer.music.load(nextMusic.encode())
                print('Now playing: ' + playlist[num])
                pygame.mixer.music.play(1)
                if len(playlist)-1 == num:
                    num = 0
                else:
                    num = num + 1
            else:
                if nowPlaying != nextMusic:
                    return
                time.sleep(0.1)

def playNext(index): # -1 上一首 1 下一首
    global playing
    if not (index == -1 or index == 1):
        return
    if not playing:
        playing = True
    global num
    num = num + index - 1
    if num == len(playlist):
        num = 0
    elif num == -1:
        num = len(playlist) - 1
    pygame.mixer.music.stop()
    t = threading.Thread(target=playMusic)
    t.start()

def adjustVolume(value): # 变化相对值 总值0~100
    global volume
    volume = volume + value
    if volume < 0:
        volume = 0
    elif volume > 100:
        volume = 100
    os.system('amixer set Master ' + str(volume) + '%')

def randomPlaylist():
    global randomOrder
    global playlist
    if not randomOrder:
        random.shuffle(playlist)
        randomOrder = True
    else:
        loadPlaylist()
        randomOrder = False

def pause():
    global playing
    if playing:
        pygame.mixer.music.pause()
        playing = False
    else:
        pygame.mixer.music.unpause()
        playing = True

def startPlay():
    t = threading.Thread(target=playMusic)
    t.start()

initPlayer()
loadPlaylist()

startPlay()

class PAJ7620U2(object):
    def __init__(self,address=PAJ7620U2_I2C_ADDRESS):
        self._address = address
        self._bus = smbus.SMBus(1)
        time.sleep(0.5)# 此处延长时间也不行
        if self._read_byte(0x00) == 0x20:
            print("\nGesture Sensor OK\n")
            for num in range(len(Init_Register_Array)):
                self._write_byte(Init_Register_Array[num][0],Init_Register_Array[num][1])
        else:
            print("\nGesture Sensor Error\n")
        # 通过设置检测点在1.log看出self._read_byte(0x00)和self._write_byte都会中断执行
        self._write_byte(PAJ_BANK_SELECT, 0)
        for num in range(len(Init_Gesture_Array)):
                self._write_byte(Init_Gesture_Array[num][0],Init_Gesture_Array[num][1])
    def _read_byte(self,cmd):
        return self._bus.read_byte_data(self._address,cmd)
    
    def _read_u16(self,cmd):
        LSB = self._bus.read_byte_data(self._address,cmd)
        MSB = self._bus.read_byte_data(self._address,cmd+1)
        return (MSB << 8) + LSB
    def _write_byte(self,cmd,val):
        self._bus.write_byte_data(self._address,cmd,val)
    def check_gesture(self):
        Gesture_Data=self._read_u16(PAJ_INT_FLAG1)
        if Gesture_Data == PAJ_UP:
            adjustVolume(5)
        elif Gesture_Data == PAJ_DOWN:
            adjustVolume(-5)
        elif Gesture_Data == PAJ_LEFT:
            playNext(-1)   
        elif Gesture_Data == PAJ_RIGHT:
            playNext(1)  
        elif Gesture_Data == PAJ_FORWARD:
            pause()
            print("Forward\r\n")
        elif Gesture_Data == PAJ_BACKWARD:
            print("Backward\r\n")
        elif Gesture_Data == PAJ_CLOCKWISE:
            randomPlaylist()
            print("Clockwise\r\n")  
        elif Gesture_Data == PAJ_COUNT_CLOCKWISE:
            print("AntiClockwise\r\n")  
        elif Gesture_Data == PAJ_WAVE:
            print("Wave\r\n")   
        return Gesture_Data

if __name__ == '__main__':
    
    import time

    print("\nGesture Sensor Test Program ...\n")

    paj7620u2=PAJ7620U2()

    while True:
        time.sleep(0.05)
        paj7620u2.check_gesture()
        





