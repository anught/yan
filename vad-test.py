#!usr/bin/env python
# coding=utf-8

import numpy as np
from pyaudio import PyAudio, paInt16, paContinue
from datetime import datetime
import wave
from tkinter import *
import os
import subprocess
import threading
import time
import webrtcvad
import collections
from array import array

# define of params
RATE = 16000
CHUNK_DURATION_MS = 20
CHUNK_SIZE = int(RATE*CHUNK_DURATION_MS / 1000)
PADDING_DURATION_MS = 1500   # 1 sec jugement

CHUNK_BYTES = CHUNK_SIZE * 2  # 16bit = 2 bytes, PCM
NUM_PADDING_CHUNKS = int(PADDING_DURATION_MS / CHUNK_DURATION_MS)
# NUM_WINDOW_CHUNKS = int(240 / CHUNK_DURATION_MS)
NUM_WINDOW_CHUNKS = int(400 / CHUNK_DURATION_MS)  # 400 ms/ 30ms  ge
NUM_WINDOW_CHUNKS_END = NUM_WINDOW_CHUNKS * 2

framerate = 16000

#NUM_SAMPLES = 2000
#framerate = 8000
channels = 1
sampwidth = 2
# record time
TIME = 3

root = Tk()
root.title("VAD TIME MEASURE TOOL")
root.geometry('500x700')  # 是x 不是*
root.resizable(width=True, height=False)  # 宽不可变, 高可变,默认为True\

label = Label(root)
label['text'] = '详细结果展示'
label.pack()
t = Text()
t.pack()

label = Label(root)
label['text'] = '待播放文件'
label.pack()
var_playfile = StringVar()
e = Entry(root, textvariable = var_playfile)
var_playfile.set("c:\\source.wav")
e.pack(ipadx=180,ipady=5)

label = Label(root)
label['text'] = '单次检测超时时间'
label.pack()
var_timeout = StringVar()
e = Entry(root, textvariable = var_timeout)
var_timeout.set("3")
e.pack(ipadx=180,ipady=5)

label = Label(root)
label['text'] = '播放完成后继续录音时间'
label.pack()
var_recordlast = StringVar()
e = Entry(root, textvariable = var_recordlast)
var_recordlast.set("1")
e.pack(ipadx=180,ipady=5)

label = Label(root)
label['text'] = '检测次数'
label.pack()
var_num = StringVar()
e = Entry(root, textvariable =var_num)
var_num.set("1")
e.pack(ipadx=180,ipady=5)

label = Label(root)
label['text'] = '录音设备编号'
label.pack()
var_recorddevidx = StringVar()
e = Entry(root, textvariable = var_recorddevidx)
var_recorddevidx.set("0")
e.pack(ipadx=180,ipady=5)

wf = None

def save_wave_file(filename, data):
    '''''save the date to the wav file'''
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    # 3.3    的join函数需要使用unicode格式的参数
    wf.writeframes(b''.join(data))
    wf.close()


def my_button(root, label_text, button_text, button_func):
    '''''''function of creat label and button'''
    # label details
    label = Label(root)
    label['text'] = label_text
    label.pack()
    # label details
    button = Button(root)
    button['text'] = button_text
    button['command'] = button_func
    button.pack()

total_time = 0
success_num = 0
fail_num = 0

def start_mesrure_callback():
    #playandrecord()
    global total_time
    global success_num
    global fail_num
    total_time = 0
    success_num = 0
    fail_num = 0

    global stop_flag
    stop_flag = False
    thread1=threading.Thread(target=playandmesrure,args=())
    thread1.setDaemon(True)
    thread1.start()

is_save_file = False
def start_mesrure_save_callback():
    global total_time
    global success_num
    global fail_num
    global is_save_file

    is_save_file = True
    total_time = 0
    success_num = 0
    fail_num = 0

    global stop_flag
    stop_flag = False
    thread1=threading.Thread(target=playandmesrure,args=())
    thread1.setDaemon(True)
    thread1.start()


stop_flag = False
def button_end_callback():
    global stop_flag
    stop_flag = True
    print('stop \n')

def callback(in_data, frame_count, time_info, status):
    global wf
    data = wf.readframes(frame_count)
    return (data, paContinue)



def playandmesrure():
    global var_recordlast
    delaytime = int(var_recordlast.get())

    mesrure_num = int(var_num.get())
    for mesrure_index in range(mesrure_num) :
        if stop_flag:break
        playandrecord(mesrure_index)
        time.sleep(delaytime)

    if success_num == 0:
        avg_time=0
    else:
        avg_time = float(total_time/success_num)
    t.insert('1.0', "index: time(ms)\n")
    t.insert('1.0', "fail num:{0}; success num:{1}\n".format(fail_num,success_num ))
    t.insert('1.0', "\navg time:{0} ms\n".format(avg_time))

def playandrecord(mesrure_index):
    global t
    global wf
    global var_recordlast
    global var_timeout
    global var_recorddevidx

    global stop_flag
    global total_time
    global success_num
    global fail_num

    if False == os.path.exists(var_playfile.get()):
        t.insert('1.0', "{0} do not exist\n".format(var_playfile.get()))
        return

    wf = wave.open(var_playfile.get(), 'rb')
    pao = PyAudio()

    # 打开声音输出流

    streamo = pao.open(format=pao.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback)
    streamo.start_stream()

    delaytime = int(var_recordlast.get())
     # long running

    vad = webrtcvad.Vad(1)
    #pai = PyAudio()

    try:
        pai = PyAudio()
        deviceidx = int(var_recorddevidx.get())
        streami = pai.open(format=paInt16, channels=1,
                           rate=framerate, input=True,
                           input_device_index=deviceidx,
                           frames_per_buffer=CHUNK_SIZE)
    except Exception as e:
        t.insert('1.0', "open record device error: {0}\n".format(e))
        return

    ring_buffer = collections.deque(maxlen=NUM_PADDING_CHUNKS)
    triggered = False
    got_a_sentence = False
    voiced_frames = []
    ring_buffer_flags = [0] * NUM_WINDOW_CHUNKS
    ring_buffer_index = 0

    ring_buffer_flags_end = [0] * NUM_WINDOW_CHUNKS_END
    ring_buffer_index_end = 0
    buffer_in = ''
    # WangS
    raw_data = array('h')
    index = 0

    print("* recording: ")
    streami.start_stream()
    save_buffer = []
    starttime = datetime.now()
    starttime_delay = 0
    time_out = int(var_timeout.get())
    while not got_a_sentence:
        chunk = streami.read(CHUNK_SIZE)
        save_buffer.append(chunk)

        active = vad.is_speech(chunk,framerate)
        endtime = datetime.now()
        ring_buffer_flags[ring_buffer_index] = 1 if active else 0
        ring_buffer_index += 1
        ring_buffer_index %= NUM_WINDOW_CHUNKS

        ring_buffer_flags_end[ring_buffer_index_end] = 1 if active else 0
        ring_buffer_index_end += 1
        ring_buffer_index_end %= NUM_WINDOW_CHUNKS_END

        # start point detection
        if not triggered:
            ring_buffer.append(chunk)
            num_voiced = sum(ring_buffer_flags)
            #print(num_voiced)
            if num_voiced > 0.7 * NUM_WINDOW_CHUNKS:
                #sys.stdout.write(' Open ')
                triggered = True
                #start_point = index - CHUNK_SIZE * 20  # start point
                # voiced_frames.extend(ring_buffer)

                time_1 = (endtime - starttime).seconds * 1000000 + (endtime - starttime).microseconds
                t.insert('1.0', "%4d : %f ms\n" % (mesrure_index, float(time_1 / 1000)))
                total_time += (time_1/1000)
                success_num +=1
                ring_buffer.clear()
                if not is_save_file:
                    break
            elif ((endtime - starttime).seconds * 1000000 + (endtime - starttime).microseconds) > time_out * 1000000:
                t.insert('1.0', "{0}: {1}\n".format(mesrure_index+1, 'timeout'))
                #list_measure_time.append("timeout")
                fail_num +=1
                triggered = True
                if not is_save_file:
                    break
        # end point detection
        '''
        else:
                # voiced_frames.append(chunk)
            ring_buffer.append(chunk)
            num_unvoiced = NUM_WINDOW_CHUNKS_END - sum(ring_buffer_flags_end)
            if num_unvoiced > 0.90 * NUM_WINDOW_CHUNKS_END:# or TimeUse > 10000000:
                #sys.stdout.write(' Close ')
                triggered = False
                #got_a_sentence = True
                t.insert('1.0', "end point\n")
        '''
        if is_save_file:
            if streamo.is_active() == False:
                if starttime_delay == 0:
                    starttime_delay = datetime.now()
                endtime = datetime.now()
                if ((endtime - starttime_delay).seconds*1000000+(endtime - starttime_delay).microseconds)>delaytime*1000000:
                    break

    streamo.close()
    pao.terminate()

    if is_save_file:
        filename = datetime.now().strftime("%Y-%m-%d_%H_%M_%S") + ".wav"
        save_wave_file(filename, save_buffer)
        t.insert('1.0', "{0} saved\n".format(filename))
    streami.close()
    pai.terminate()
    #start to PESQ
    #PESQ_Calc(filename)
    #return filename

def PESQ_Calc(recordfilename):
    PESQCMD = 'PESQ.exe'
    PESQFULLPATH = "{0}\\{1}".format(os.getcwd(), PESQCMD)
    pesqcalc = '{0} +8000 {1} {2}'.format(PESQFULLPATH, var_playfile.get(), recordfilename)
    print('before\n')
    sub=subprocess.Popen(pesqcalc,shell=True,stdout=subprocess.PIPE)
    resultstr = sub.stdout.read()
    resultstr = resultstr.decode()
    resultidx = resultstr.rfind('PESQ_MOS = ')
    resultstr = resultstr[resultidx:]
    t.insert('1.0', "{0} {1}".format(recordfilename, str(resultstr)))

def main():
    #my_button(root, "放音同时进行检测", "START", button_callback)
    #my_button(root, "停止检测", "END", button_end_callback)
    Button(root, text="放音同时进行检测", fg="blue", bd=2, width=28, command=start_mesrure_callback).pack()
    Button(root, text="放音同时进行检测，并保存录音文件", fg="blue", bd=2, width=28, command=start_mesrure_save_callback).pack()
    Button(root, text="停止检测", width=19, relief=GROOVE, bg="red",command=button_end_callback).pack()
    root.mainloop()


  #  while True:
   #     time.sleep(10)
if __name__ == "__main__":
    main()
