import openai

openai.api_key = open("api_key.txt", "r").read().strip()
audio_file= open("sample_audio.m4a", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
print(transcript)