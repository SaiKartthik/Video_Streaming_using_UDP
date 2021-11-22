from socket import socket
import cv2
import socket
from tkinter import *
import os
from PIL import Image, ImageTk
import base64
import numpy as np
import time
thumbnaillist=[]
def video_stream(b):
    print(b)
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
    print("working")



def on_closing(tp):
    print("closed")
    tp.destroy()
    client_socket.close()
def addthumbnail(tp,b,i):
    label12=Button(tp,text=i,command=lambda:video_stream(i)).place(x=0,y=b)
def gui():
    tp=Tk()
    tp.geometry("500x500")
    tp.protocol("WM_DELETE_WINDOW",lambda:on_closing(tp))
    a=0
    b=0
    for i in thumbnaillist:
        addthumbnail(tp,b,i)
        image = Image.open(i)
        resize_image = image.resize((200,200))
        img = ImageTk.PhotoImage(resize_image)
        b=b+20
    sb = Scrollbar(tp)
    sb.pack( side = RIGHT,fill = Y )
    tp.mainloop()
BUFF_SIZE=65536
client_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_ip=socket.gethostname()
port=9688
message="hello"
message=message.encode('ASCII')
client_socket.sendto(message,(host_ip,port))
x,_=client_socket.recvfrom(BUFF_SIZE)
x=int.from_bytes(x,'big')
print(x)
cnt=0
while cnt<x:
    y,_=client_socket.recvfrom(BUFF_SIZE)
    y=y.decode('ASCII')
    thumbnaillist.append(y)
    cnt+=1
gui()

#
