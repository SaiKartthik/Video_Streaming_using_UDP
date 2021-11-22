import cv2,imutils
import socket
import os
import base64
import time
videolist=[]
audiolist=[]
thumbnaillist=[]
dir_path=os.path.dirname(os.path.realpath(__file__))
for root,dirs,files in os.walk(dir_path):
    for file in files:
	    if file.endswith(".mp4"):
		    videolist.append(file)

for i in videolist:
    x=len(i)
    y=i[0:x-4]+".wav"
    audiolist.append(y)
for i in videolist:
    x=len(i)
    y=i[0:x-4]+".PNG"
    thumbnaillist.append(y)
BUFF_SIZE=65536
server_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '192.168.56.1'
port=9688
server_addr=(host_ip,port)
server_socket.bind(server_addr)
print("waiting for connection at:",server_addr)
def video_stream(client_addr):
    while True:
        file_name,_=server_socket.recvfrom(BUFF_SIZE)
        file_name=file_name.decode('ASCII')
        print(file_name)
        file_name=file_name[:len(file_name)-4]+".mp4"
        file_name1=cv2.VideoCapture(file_name)
        lenth=int(file_name1.get(cv2.CAP_PROP_FRAME_COUNT))
        file_name1.release()
        lenth1=lenth.to_bytes(2,'big')
        server_socket.sendto(lenth1,client_addr)
        cnt1=0
        file_name1=cv2.VideoCapture(file_name)
        FPS = file_name1.get(cv2.CAP_PROP_FPS)
        TS = (0.5/FPS)
        fps,st,frames_to_count,cnt = (0,0,20,0)
        WIDTH=400
        while cnt1<lenth:
            _,frame=file_name1.read()
            frame=imutils.resize(frame,width=WIDTH)
            encoded,buffer=cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
            message = base64.b64encode(buffer)
            server_socket.sendto(message,client_addr)
            frame = cv2.putText(frame,'FPS: '+str(round(fps,1)),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
            cv2.imshow('TRANSMITTING VIDEO',frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                os._exit(1)
                break
            if cnt == frames_to_count:
                try:
                    fps = round(frames_to_count/(time.time()-st))
                    print(fps)
                    st=time.time()
                    cnt=0
                except:
                    break
            cnt+=1
            cnt1=cnt1+1
            if(cnt1==lenth):
                cv2.destroyAllWindows()
                break

def connections():
    msg,client_add=server_socket.recvfrom(BUFF_SIZE)
    print(msg)
    x=len(thumbnaillist)
    x=x.to_bytes(2,'big')
    server_socket.sendto(x,client_add)
    for i in thumbnaillist:
        print(i)
        i=i.encode('ASCII')
        server_socket.sendto(i,client_add)
    video_stream(client_add)
while True:
    connections()
