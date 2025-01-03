import cv2
import urllib.request
import numpy as np
import os
from datetime import datetime
import face_recognition
import requests
from PIL import Image, ImageTk
import customtkinter as tk
from customtkinter import CTkLabel as Label
from customtkinter import CTkButton as Button
from customtkinter import CTkEntry as Entry
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Path to the image folder
path = 'image_folder'

# Get the Telegram API token and chat ID from the environment variables
api_token = os.getenv('TELEGRAM_API_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

if not api_token:
    raise ValueError("Telegram API token is not set. Please add it to the .env file.")

if not chat_id:
    raise ValueError("Telegram chat ID is not set. Please add it to the .env file.")

# Function to send a photo to Telegram
def sendPhoto(image):
    url = f'https://api.telegram.org/bot{api_token}/sendPhoto'
    temp_filename = 'temp_image.jpg'
    cv2.imwrite(temp_filename, image)
    with open(temp_filename, 'rb') as photo:
        files = {'photo': photo}
        params = {'chat_id': chat_id}
        response = requests.post(url, files=files, params=params)
    if response.status_code == 200:
        print('Photo sent successfully!')
    else:
        print('Failed to send photo.')

# Load images and create encodings
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)
print('Encoding Complete')

# Process a video frame
def process_frame():
    img_resp = urllib.request.urlopen(url)
    imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
    img = cv2.imdecode(imgnp, -1)
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            requests.get(urlOn)
        else:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
            cv2.putText(img, "Intruder!!!", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            print("Intruder")
            sendPhoto(img)
            requests.get(buzzOn)

    cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    panel.imgtk = imgtk
    panel.configure(image=imgtk)
    panel.after(1, process_frame)

# Start video processing
def start_processing():
    global url, urlOn, urlOff, buzzOn, buzzOff
    ip_address = ip_entry.get()
    url = f'http://{ip_address}/cam-hi.jpg'
    urlOn = f'http://{ip_address}/lock/1'
    buzzOn = f'http://{ip_address}/buzz/1'
    root.after(1, process_frame)

# Create GUI
root = tk.CTk()
root.title("ESP32Cam Security System")

input_frame = tk.CTkFrame(root)
input_frame.pack(pady=10)

ip_label = Label(input_frame, text="IP Address:", font=('Arial', 14))
ip_label.grid(row=0, column=0)

ip_entry = Entry(input_frame, font=('Arial', 14))
ip_entry.grid(row=0, column=1)

start_button = Button(root, text="Start", command=start_processing, font=('Arial', 14))
start_button.pack(pady=10)

panel = Label(root, text="", font=('Arial', 14))
panel.pack(padx=10, pady=10)

root.mainloop()
