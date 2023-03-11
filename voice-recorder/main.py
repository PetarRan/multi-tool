import sounddevice
from scipy.io.wavfile import write

fs=44100 #Sample rate
second=int(input("Enter the duration of your recording in seconds:"))
print("Recording . . .")

record_voice=sounddevice.rec(int(second * fs), samplerate=fs, channels=2)
sounddevice.wait()

write("recording.wav", fs, record_voice)
print("Finished Recording!")