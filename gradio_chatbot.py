import gradio as gr
import random
import time

with gr.Blocks() as demo:
    gr.Markdown("## Heading level 2")
    gr.Markdown("#### Heading level 4")
    chatbot = gr.Chatbot(lines=4, label="Interview Chatbot", placeholder="Type a message..")
    msg = gr.Textbox(lines=4, placeholder="Initial message..")
    clear = gr.Button("Clear")

    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history):
        last_message = history[-1][0]
        bot_message = last_message + "is cool!"
        history[-1][1] = bot_message
        return history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch()