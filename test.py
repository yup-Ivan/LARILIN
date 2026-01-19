import requests

url = "http://127.0.0.1:5000/lara/save_record"

files = {
    "audio_data": open("prueba.wav", "rb")
}

data = {
    "model": "whisper-base"
}

r = requests.post(url, files=files, data=data)

print(r.status_code)
print(r.text)
