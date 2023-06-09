import gradio as gr
import openai
from pydub import AudioSegment


openai.api_key = open("api_key.txt", "r").read().strip()

def convert_audio_file(input_file_path, output_file_path, output_format):
    audio = AudioSegment.from_file(input_file_path)
    audio.export(output_file_path, format=output_format)
    return output_file_path


def whisper_transcribe(input_filepath):
    output_filepath = "/Users/kshitij.jain/Desktop/ChatGPT_Experiments/python_chatgpt/newaudiofile.mp3"
    output_filepath = convert_audio_file(input_filepath, output_filepath, "mp3")
    audio_file= open(output_filepath, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]
    
with gr.Blocks() as demo:
    audio_input = gr.Audio(source="microphone", type="filepath")
    text_output = gr.Textbox()
    transcribe_button = gr.Button("Transcribe")

    transcribe_button.click(whisper_transcribe, audio_input, text_output)

demo.launch()
    