import pyaudio
import speech_recognition as sr
import requests
import time
import pyttsx3
import datetime
import serial
import mysql.connector

# Paramètres PyAudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Clé API pour OpenWeatherMap
api_key = "c5deb81a5b0870c1ff180fd7fb9cf81f"

# Initialisation de pyttsx3
engine = pyttsx3.init()
engine.setProperty('voice', 'french')

# Configuration du port série pour l'Arduino
serial_port = '/dev/rfcomm0'
baud_rate = 9600

# Connexion à la base de données MySQL
mydb = mysql.connector.connect(
    host="192.168.0.122",
    user="bilal",
    password="Bilal13112004?",
    database="STATION_METEO"
)

# Fonction pour envoyer des commandes à l'Arduino
def send_command_to_arduino(command):
    try:
        with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
            ser.write(command.encode())
            print(f"Envoyé à l'Arduino : {command}")
    except serial.SerialException as e:
        print(f"Erreur de communication avec l'Arduino : {e}")

# Fonction pour obtenir l'index du microphone
def get_microphone_index():
    mic_list = sr.Microphone.list_microphone_names()
    if not mic_list:
        print("Aucun microphone détecté sur votre système.")
        return None

    print("Liste des microphones disponibles :")
    for index, name in enumerate(mic_list):
        print(f"Microphone index {index}: {name}")

    while True:
        try:
            selected_index = int(input("Entrez l'index du microphone à utiliser : "))
            if selected_index < 0 or selected_index >= len(mic_list):
                print("Index invalide. Veuillez entrer un index valide.")
            else:
                return selected_index
        except ValueError:
            print("Veuillez entrer un nombre entier pour l'index du microphone.")

# Fonction pour reconnaître la parole
def recognize_speech(microphone_index):
    r = sr.Recognizer()
    try:
        with sr.Microphone(device_index=microphone_index) as source:
            print("Ajustement du bruit ambiant...")
            r.adjust_for_ambient_noise(source)
            print("Dites quelque chose :")
            audio = r.listen(source)
            try:
                command = r.recognize_google(audio, language='fr-FR')
                print("Vous avez dit : " + command)
                return command.lower()
            except sr.UnknownValueError:
                print("La reconnaissance de la parole a échoué")
                return ""
            except sr.RequestError as e:
                print(f"Erreur lors de la reconnaissance de la parole : {e}")
                return ""
    except AssertionError as e:
        print(f"Erreur lors de l'accès au microphone : {e}")
        return ""
    except Exception as e:
        print(f"Une erreur s'est produite lors de la reconnaissance de la parole : {e}")
        return ""

# Fonction pour gérer les commandes
def handle_command(command):
    if "quel temps fait-il" in command:
        town = command.split("à")[-1].strip()
        url = f"http://api.openweathermap.org/data/2.5/weather?q={town}&appid={api_key}&units=metric&lang=fr"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            response_text = f"À {town}, il fait {temp} degrés avec {description}"
            print(response_text)
            speak(response_text)
        else:
            response_text = f"La ville {town} n'a pas été trouvée."
            print(response_text)
            speak(response_text)
    elif "bonjour" in command:
        response_text = "Bonjour!"
        print(response_text)
        speak(response_text)
    elif "au revoir" in command or "tu peux t'éteindre" in command:
        response_text = "Au revoir!"
        print(response_text)
        speak(response_text)
        return False  # Arrêter le programme
    elif "heure" in command:
        current_time = datetime.datetime.now().strftime("%H:%M")
        response_text = f"Il est {current_time} actuellement."
        print(response_text)
        speak(response_text)
    elif "date" in command:
        current_date = datetime.datetime.now().strftime("%d/%m/%Y")
        response_text = f"Aujourd'hui, nous sommes le {current_date}."
        print(response_text)
        speak(response_text)
    elif "ferme le store" in command:
        response_text = "Fermeture du store."
        print(response_text)
        speak(response_text)
        send_command_to_arduino('1')
    elif "ouvre le store" in command:
        response_text = "Ouverture du store."
        print(response_text)
        speak(response_text)
        send_command_to_arduino('0')
    elif "quelle est la température intérieure" in command:
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM valeur ")
        result = cursor.fetchone()
        if result:
            temperature = result[1]
            response_text = f"La température intérieure est de {temperature} degrés Celsius."
            print(response_text)
            speak(response_text)
    elif "quelle est la température extérieure" in command:
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM valeur ")
        result1 = cursor.fetchone()
        if result1:
            temperature1 = result1[2]
            response_text = f"La température extérieure est de {temperature1} degrés Celsius."
            print(response_text)
            speak(response_text)
        else:
            response_text = "La température intérieure n'est pas disponible pour le moment."
            print(response_text)
            speak(response_text)
        cursor.close()
    else:
        response_text = "Commande non reconnue"
        print(response_text)
        speak(response_text)
    return True  # Continuer à exécuter le programme

# Fonction pour parler
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Obtenir l'index du microphone
microphone_index = get_microphone_index()

# Boucle principale pour gérer la reconnaissance de la parole
running = True
while running:
    # Reconnaître la parole
    if microphone_index is not None:
        command = recognize_speech(microphone_index)
        if command:
            # Gérer la commande
            running = handle_command(command)
        else:
            # Si la reconnaissance vocale n'a pas compris la commande
            response_text = "Je n'ai pas compris."
            print(response_text)
            speak(response_text)
    else:
        print("Microphone non initialisé.")
        break

    time.sleep(1)

# Fermeture de la connexion à la base de données
mydb.close()
