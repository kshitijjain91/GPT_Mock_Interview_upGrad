# text to speech test with gTTS
from gtts import gTTS

text = '''
Can you briefly describe the difference between supervised and unsupervised learning techniques? 
Provide one example of each.
'''
language = "en"

speech = gTTS(text = text, lang = language, slow = False)
speech.save("text_to_speech_sample.mp3")