import cv2,imutils
import socket
import os
import base64
import time
import wave,pyaudio

#Collecting files in that folder and storing them in List
videolist=[]
audiolist=[]
thumbnaillist=[]

#Checking throught the directories
dir_path=os.path.dirname(os.path.realpath(__file__))
for root,dirs,files in os.walk(dir_path):
    for file in files:
	    if file.endswith(".mp4"):
		    videolist.append(file)

#Collecting .wav files for audio
for i in videolist:
    x=len(i)
    y=i[0:x-4]+".wav"
    audiolist.append(y)

#Checking .png files for thumbnails
for i in videolist:
    x=len(i)
    y=i[0:x-4]+".PNG"
    thumbnaillist.append(y)


BUFF_SIZE=65536 #Creating a buffersize of 65536

#Creating a server
server_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '192.168.56.1'
port = 9999
server_addr=(host_ip,port)
server_socket.bind(server_addr)
print("waiting for connection at:",server_addr)

def video(client_addr):
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
        print(FPS)
        TS = (0.5/FPS)
        fps,st,frames_to_count,cnt = (0,0,20,0)
        WIDTH=400

        while cnt1<lenth:
            cv2.waitKey(1)
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
                    st=time.time()
                    cnt=0
                except:
                    break
            cnt+=1
            cnt1=cnt1+1
            if(cnt1==lenth):
                cv2.destroyAllWindows()
                break

def audio():
    while True:
        serveraudio_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        serveraudio_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
        serveraudio_socket.bind((host_ip,port-1))
        message12,clientadd=serveraudio_socket.recvfrom(BUFF_SIZE)
        message12=message12.decode('ASCII')
        print(message12)
        CHUNK = 10*1024
        wf = wave.open(message12)
        n=wf.getnframes()
        n1=str(n)
        n1=n1.encode('ASCII')
        serveraudio_socket.sendto(n1,clientadd)
        p = pyaudio.PyAudio()
        print('server listening at',(host_ip, (port)),wf.getframerate())
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),channels=wf.getnchannels(),rate=wf.getframerate(),input=True,frames_per_buffer=CHUNK)
        data = None
        sample_rate = wf.getframerate()
        cnt1=0
        print(n)
        print(n/CHUNK)
        
        while cnt1<(n/CHUNK):
                data = wf.readframes(CHUNK)
                serveraudio_socket.sendto(data,clientadd)
                time.sleep(0.8*CHUNK/sample_rate)
                cnt1+=1

def connection():
    msg,client_add=server_socket.recvfrom(BUFF_SIZE)
    print(msg)
    x=len(thumbnaillist)
    x=x.to_bytes(2,'big')
    server_socket.sendto(x,client_add)
    for i in thumbnaillist:
        print(i)
        i=i.encode('ASCII')
        server_socket.sendto(i,client_add)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as executor1:
        executor1.submit(video,(client_add))
        executor1.submit(audio)

while True:
    connection()
