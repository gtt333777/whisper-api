
import sys
import os
import librosa
import music21
import requests
import firebase_admin
from firebase_admin import credentials, storage

# Firebase Setup
cred = credentials.Certificate('firebase-service-account.json')
firebase_admin.initialize_app(cred, {'storageBucket': 'YOUR_PROJECT_ID.appspot.com'})

def download_file(url, filename):
    r = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(r.content)

def convert_to_midi(mp3_file, midi_file):
    y, sr = librosa.load(mp3_file)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
    midi = music21.stream.Stream()
    duration = 0.5

    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    for t in range(0, pitches.shape[1], 100):
        index = magnitudes[:, t].argmax()
        freq = pitches[index, t]
        if freq > 0:
            note = music21.note.Note()
            note.pitch.frequency = freq
            note.quarterLength = duration
            midi.append(note)
    midi.write("midi", fp=midi_file)

def upload_to_firebase(midi_path, output_name):
    bucket = storage.bucket()
    blob = bucket.blob(f"midi/{output_name}.mid")
    blob.upload_from_filename(midi_path)
    blob.make_public()
    print("Uploaded to Firebase:", blob.public_url)

if __name__ == '__main__':
    mp3_url = sys.argv[1]
    output_name = sys.argv[2]
    mp3_file = "temp.mp3"
    midi_file = f"{output_name}.mid"

    download_file(mp3_url, mp3_file)
    convert_to_midi(mp3_file, midi_file)
    upload_to_firebase(midi_file, output_name)
