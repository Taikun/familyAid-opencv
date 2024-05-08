from dotenv import load_dotenv
import os
import cv2
import numpy as np
import requests
import time


def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=data)
    return response.json()


# Cargar las variables de entorno del archivo .env
load_dotenv()
# Ahora puedes acceder a las variables como variables de entorno
# Token y chat_id de tu bot de Telegram
telegram_token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('CHAT_ID')
CAMERA1_URL = os.getenv('CAMERA1_URL')
# print(f"Conectando con cámara {CAMERA1_URL} usando el token {telegram_token} con chat id {chat_id}")

cap = cv2.VideoCapture(CAMERA1_URL)


# Coordenadas y dimensiones del ROI
x, y, w, h = 1000, 1000, 1000, 1000  # Ajusta estos valores

# Crear un sustractor de fondo
backSub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=100, detectShadows=True)

cooldown_period = 10  # Tiempo en segundos entre alertas
last_alert_time = time.time() - cooldown_period
area_threshold = 1500  # Ajusta este valor según sea necesario

while cap.isOpened():
    ret, frame = cap.read()
    # Definir el ROI
    roi = frame[y:y+h, x:x+w]

    if not ret:
        break

    fgMask = backSub.apply(frame)  # Aplicar sustractor de fondo
    _, thresh = cv2.threshold(fgMask, 25, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < area_threshold:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        current_time = time.time()
        if current_time - last_alert_time > cooldown_period:
            # send_telegram_message(telegram_token, chat_id, 'Movimiento detectado!')
            last_alert_time = current_time

    cv2.imshow("Camera Feed", frame)
    # cv2.imshow("ROI", roi)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()