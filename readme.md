# GPT Mock Interview Assistant | App Overview
The GPT-powered mock interview assistant is a web application designed for learners to practice mock job interviews and be better prepared for real-world interviews. While one could modify this to simulate interviews in almost any area (via modifying the prompts, more on that below), in upGrad’s context, we are designing the app for interviews in Data Science, Digital Marketing, Full Stack Development, Product Management, Human Resources, Law etc. 

[Here](https://www.linkedin.com/posts/mayank-kumar-5573243_education-technology-learning-activity-7046334211317710848-CcOR?utm_source=share&utm_medium=member_desktop) is a short video demo of the app. There are three key functionalities of the app:
1. Process user input: Given a question asked by the GPT Interview Assistant, the user submits a response either via text directly or via speech. 
2. Ask questions: The Assistant asks follow up questions or provides hints depending on the user’s response. It continues this dialogue for a maximum of n question-response pairs (n = 25 currently)
3. Provide score and feedback: At the end of the interview, the Assistant provides feedback and score (1-10) for each response

The app is written in Python and deployed on a [Hugging Face](https://upgradgpt-gpt-interview-beta.hf.space/) server. Frontend is built using [Gradio](https://gradio.app/), a Python library used to build simple web applications. The database is AWS RDS which stores all conversion history, grades and feedback.  

The sections below describe the design and architecture of each of the functionalities. 

# App Architecture
## Processing User Input
This is a simple textbox that accepts the user’s response. Most users prefer to record their audio via mic which is then transcribed into the textbox. The transcription is done using the [Whisper Text-to-Speech API](https://platform.openai.com/docs/guides/speech-to-text) by OpenAI. 

In initial testing, we have found that the transcription accuracy of Whisper is impressively good (with various accents, background noise typical in an office setting, etc). Sometimes (< 2-3%) it is unable to correctly transcribe contextual / technical terms and phrases (e.g. K-means clustering, bias-variance tradeoff etc). In the future, we plan to improve the transcription accuracy to almost 100% using [prompting as described here](https://platform.openai.com/docs/guides/speech-to-text/prompting).

The recorded audio files are stored on the server, though each audio input is overwritten by the next one to save disk space. For e.g. if an interview length is 20 question-response pairs, only one audio file will be created on the server (instead of 20). The transcribed text is stored in an AWS database, and hence all conversations are retrievable.


## Asking Questions 
This is the core functionality of the application – the Assistant tries to simulate a long conversation with the user, ask questions in a flow, and provide cues and direction when the user needs them. 

Fortunately, ChatGPT is really good at making chats (no surprises here 🙂). All we need to do is:
* Provide prompts / directions to guide the behavior of ChatGPT
* Store and provide the entire chat history as input (so it can process the next response in the context of the entire chat). 

Because it is capable of using the entire chat history to generate each response, it reflects in the conversion flow. For e.g. if the user enters good responses in the interview, it progressively asks better / harder questions. While if the user seems to struggle with some questions, it provides more hints and increases the difficulty level gradually.




