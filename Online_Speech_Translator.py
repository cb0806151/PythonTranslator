import pyaudio
import wave
import keyboard
import speech_recognition as sr
from googletrans import Translator
from playsound import playsound
from gtts import gTTS
from pynput.keyboard import Key, Listener


class SpeechTranslator():
    def __init__(self):
        self.sample_chunks = 1024
        self.sample_bit_count = pyaudio.paInt16
        self.samples_per_second = 44100
        self.channels = 2
        self.seconds = 30
        self.file_name = "output.wav"
        self.audiopi = pyaudio.PyAudio()
        self.audio_frames = []
        self.recording_stream = self.audiopi
        self.recording_started = False
        self.translateToLanguage = "German"
        print("Press Spacebar to start recording; press spacebar again to stop recording.")
        with Listener(on_press=self.start_recording) as listener:
            listener.join()

    def start_recording(self, key):
        if key == Key.space and self.recording_started is False:
            print("\nStarted recording")
            self.recording_started = True
            self.recording_stream = self.audiopi.open(format=self.sample_bit_count,
                                                      channels=self.channels,
                                                      rate=self.samples_per_second,
                                                      frames_per_buffer=self.sample_chunks,
                                                      input=True)

            for i in range(0, int(self.samples_per_second / self.sample_chunks * self.seconds)):
                data = self.recording_stream.read(self.sample_chunks)
                self.audio_frames.append(data)
                if keyboard.is_pressed('spacebar'):
                    self.stop_recording()
                    break

            return False

    def stop_recording(self):
        print("\nFinished recording")
        self.recording_stream.stop_stream()
        self.recording_stream.close()
        self.audiopi.terminate()
        self.save_file()

    def save_file(self):
        wave_file = wave.open(self.file_name, 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(self.audiopi.get_sample_size(self.sample_bit_count))
        wave_file.setframerate(self.samples_per_second)
        wave_file.writeframes(b''.join(self.audio_frames))
        wave_file.close()
        self.convert_recording_to_text()

    def convert_recording_to_text(self):
        print("\nConverting recording to text...")
        r = sr.Recognizer()

        audio_file_test = sr.AudioFile(self.file_name)
        with audio_file_test as source:
            audio = r.record(source)

        recording_as_text = r.recognize_google(audio)
        print('\n"' + recording_as_text + '"')
        self.translate_text_to_other_language(recording_as_text)

    def translate_text_to_other_language(self, text_to_translate):
        print("\nConverting text to " + self.translateToLanguage + "...")

        translator = Translator()
        translated_text_object = translator.translate(text_to_translate, dest='de')
        translated_text = translated_text_object.text

        print('\n"' + translated_text + '"')
        self.play_translated_text(translated_text)

    def play_translated_text(self, translated_text):
        print("\nPlaying translated text")
        tts = gTTS(text=translated_text)
        tts.save("translated_text.mp3")
        playsound("translated_text.mp3")


record = SpeechTranslator()


