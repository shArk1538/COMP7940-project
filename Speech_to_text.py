from google.cloud import speech
from pydub import AudioSegment
import os

service_account_file = './sst.json'
client = speech.SpeechClient.from_service_account_json(service_account_file)
# AudioSegment.ffmpeg = "/usr/local/lib/python3.12/site-packages/ffmpeg"

class speech2text():
    def __init__(self, audio_file_id='000'):
        self.id = audio_file_id
        self.path = f'./{self.id}.ogg'

    def process(self,language):
        audio = AudioSegment.from_file(self.path, format='ogg')  # 使用pyhub和ffmpeg库将ogg格式转换为wav格式
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)  # 16bit, 16000Hz, Mono单声道
        audio.export(f'{self.id}.wav', format='wav')

        with open(f'{self.id}.wav', 'rb') as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language
            )

        response = client.recognize(config=config, audio=audio)
        os.remove(f'{self.id}.wav')

        return response
