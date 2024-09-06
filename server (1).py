import pyaudio
import speech_recognition as sr
import requests
import time
import pyttsx3
import datetime

# Paramètres pour PyAudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

api_key = "c5deb81a5b0870c1ff180fd7fb9cf81f"

# Initialisation de pyttsx3
engine = pyttsx3.init()

# Fonction pour obtenir l'index du microphone
def get_microphone_index():
    mic_list = sr.Microphone.list_microphone_names()
    if not mic_list:
        print("Aucun microphone détecté sur votre système.")
        return None

    print("Liste des microphones disponibles :")
    for index, name in enumerate(mic_list):
        print("Microphone index {}: {}".format(index, name))

    while True:
        try:
            selected_index = int(input("Entrez l'index du microphone à utiliser : "))
            if selected_index < 0 or selected_index >= len(mic_list):
                print("Index invalide. Veuillez entrer un index valide.")
            else:
                return selected_index
        except ValueError:
            print("Veuillez entrer un nombre entier pour l'index du microphone.")

# Fonction pour obtenir l'index du périphérique de sortie
def get_output_device_index():
    p = pyaudio.PyAudio()
    print("Liste des périphériques de sortie disponibles :")
    output_device_indices = []

    for index in range(p.get_device_count()):
        info = p.get_device_info_by_index(index)
        if info["maxOutputChannels"] > 0:
            output_device_indices.append(index)
            print(f"Périphérique de sortie index {index}: {info['name']}")

    p.terminate()

    if not output_device_indices:
        print("Aucun périphérique de sortie détecté sur votre système.")
        return None

    while True:
        try:
            selected_index = int(input("Entrez l'index du périphérique de sortie à utiliser : "))
            if selected_index not in output_device_indices:
                print("Index invalide. Veuillez entrer un index valide.")
            else:
                return selected_index
        except ValueError:
            print("Veuillez entrer un nombre entier pour l'index du périphérique de sortie.")

# Fonction pour reconnaître la parole
def recognize_speech(microphone_index):
    r = sr.Recognizer()
    with sr.Microphone(device_index=microphone_index) as source:
        print("Dites quelque chose :")
        audio = r.listen(source)
        try:
            command = r.recognize_google(audio, language='fr-fr')
            print("Vous avez dit : " + command)
            return command.lower()
        except sr.UnknownValueError:
            print("La reconnaissance de la parole a échoué")
            return ""
        except sr.RequestError as e:
            print("Erreur lors de la reconnaissance de la parole : {0}".format(e))
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
    elif "au revoir" in command:
        response_text = "Au revoir!"
        print(response_text)
        speak(response_text)
        return False
    elif "tu peux t'éteindre" in command:
        response_text = "Au revoir!"
        print(response_text)
        speak(response_text)
        return False
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
    else:
        response_text = "Commande non reconnue"
        print(response_text)
        speak(response_text)
    return True

# Fonction pour parler
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Obtenir l'index du microphone
microphone_index = get_microphone_index()

# Obtenir l'index du périphérique de sortie
output_device_index = get_output_device_index()

# Vous pouvez essayer de configurer pyttsx3 pour utiliser le périphérique de sortie sélectionné
# Notez que cette fonctionnalité pourrait ne pas être directement disponible pour pyttsx3
# engine.setProperty('outputDevice', output_device_index)

# Boucle principale pour gérer la reconnaissance de la parole
running = True
while running:
    # Reconnaître la parole
    command = recognize_speech(microphone_index)
    if command:
        # Gérer la commande
        running = handle_command(command)
    else:
        # Si la reconnaissance vocale n'a pas compris la commande
        response_text = "Je n'ai pas compris."
        print(response_text)
        speak(response_text)

    time.sleep(1)

