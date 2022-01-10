#Importing required packages
from socket import socket
import cv2
import socket
from tkinter import *
import os
from PIL import Image, ImageTk
import base64
import numpy as np
import time
import wave,pyaudio
import threading,queue

#Method to decode information received from Server
def decode1(bb):
    bb=bb.decode('ASCII')
    return int(bb)
thumbnaillist=[]
q = queue.Queue(maxsize=2000)

#Joining Audio and Video
def parallel(i):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as executor1:
        executor1.submit(video,(i))
        executor1.submit(audio,(i))

#Get Audio and Related data
def audio(b1):
    print(b1)
    audioclientsocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    audioclientsocket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    message12=b1[0:len(b1)-4]+".wav"
    print(message12)
    message12=message12.encode('ASCII')
    audioclientsocket.sendto(message12,(host_ip,port-1))
    byte_len,_=audioclientsocket.recvfrom(BUFF_SIZE)
    n=byte_len.decode('ASCII')
    n1=int(n)
    p = pyaudio.PyAudio()
    CHUNK = 10*1024
    stream = p.open(format=p.get_format_from_width(2),channels=2,rate=44100,output=True,frames_per_buffer=CHUNK)
    cnt1=0

    def getAudioData():
        while cnt1<(n1/CHUNK):
            frame,_= audioclientsocket.recvfrom(BUFF_SIZE)
            q.put(frame)
            print('Queue size...',q.qsize())
            cnt1+1
    t1 = threading.Thread(target=getAudioData, args=())
    t1.start()
    time.sleep(1)
    print('Now Playing...')
    cnt2=0
    while cnt2<(n1/CHUNK):
        frame = q.get()
        stream.write(frame)
        cnt2+=1
    print('Audio closed')

#Get video and related data
def video(b):
    b=b.encode('ASCII')
    client_socket.sendto(b,(host_ip,port))
    lenth,_=client_socket.recvfrom(BUFF_SIZE)
    lenth=int.from_bytes(lenth,'big')
    print(lenth)
    fps,st,frames_to_count,cnt = (10,0,20,0)
    cnt1=0

    while cnt1<lenth:
        packet,_ = client_socket.recvfrom(BUFF_SIZE)
        data = base64.b64decode(packet,' /')
        npdata = np.frombuffer(data,dtype=np.uint8)
        frame = cv2.imdecode(npdata,1)
        frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
        cv2.imshow("RECEIVING VIDEO",frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            os._exit(1)
            break
        if cnt == frames_to_count:
            try:
                fps = round(frames_to_count/(time.time()-st))
                st=time.time()
                cnt=0
            except:
                pass
        cnt+=1
        cnt1=cnt1+1
        if cnt1==lenth:
            cv2.destroyAllWindows()
            break

#To destroy sockets
def on_closing(tp):
    print("closed")
    tp.destroy()
    client_socket.close()

#Adding images to thumbnails
def addthumbnail(tp,b,i,img):
    label12=Button(tp,image=img,command=lambda:parallel(i)).place(x=0,y=b)

#Method to display files in a GUI
def gui():
    tp=Tk()
    tp.geometry("500x500")
    tp.protocol("WM_DELETE_WINDOW",lambda:on_closing(tp))
    a=0
    b=0

    for i in thumbnaillist:
        image = Image.open(i)
        resize_image = image.resize((100,100))
        img = ImageTk.PhotoImage(resize_image)
        addthumbnail(tp,b,i,img)
        b=b+110
    sb = Scrollbar(tp)
    sb.pack( side = RIGHT,fill = Y )
    tp.mainloop()

BUFF_SIZE=65536
client_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_ip=socket.gethostname()
port=9999
message="hello"
message=message.encode('ASCII')
client_socket.sendto(message,(host_ip,port))
x,_=client_socket.recvfrom(BUFF_SIZE)
x=int.from_bytes(x,'big')
print("No of files found : ",x)
cnt=0

while cnt<x:
    y,_=client_socket.recvfrom(BUFF_SIZE)
    y=y.decode('ASCII')
    thumbnaillist.append(y)
    cnt+=1
gui()
