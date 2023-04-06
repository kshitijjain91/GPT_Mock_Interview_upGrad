# GPT Mock Interview Assistant | App Overview
The GPT-powered mock interview assistant is a web application designed for learners to practice mock job interviews and be better prepared for real-world interviews. While one could modify this to simulate interviews in almost any area (via modifying the prompts, more on that below), in upGrad’s context, we are designing the app for interviews in Data Science, Digital Marketing, Full Stack Development, Product Management, Human Resources, Law etc. 

[Here](https://www.linkedin.com/posts/mayank-kumar-5573243_education-technology-learning-activity-7046334211317710848-CcOR?utm_source=share&utm_medium=member_desktop) is a short video demo of the app. There are three key functionalities of the app:
1. **Process user input:** Given a question asked by the GPT Interview Assistant, the user submits a response either via text directly or via speech. 
2. **Ask questions:** The Assistant asks follow up questions or provides hints depending on the user’s response. It continues this dialogue for a maximum of n question-response pairs (n = 25 currently)
3. **Provide score and feedback:** At the end of the interview, the Assistant provides feedback and score (1-10) for each response

The app is written in Python and deployed on a [Hugging Face](https://upgradgpt-gpt-interview-beta.hf.space/) server. Frontend is built using [Gradio](https://gradio.app/), a Python library used to build simple web applications. The database is AWS RDS which stores all conversion history, grades and feedback.  

The sections below describe the design and architecture of each of the functionalities. 

# App Architecture
## Processing User Input
This is a simple textbox that accepts the user’s response. Most users prefer to record their audio via mic which is then transcribed into the textbox. The transcription is done using the [Whisper Text-to-Speech API](https://platform.openai.com/docs/guides/speech-to-text) by OpenAI. 

In initial testing, we have found that the transcription accuracy of Whisper is impressively good (with various accents, background noise typical in an office setting, etc). Sometimes (< 2-3%) it is unable to correctly transcribe contextual / technical terms and phrases (e.g. K-means clustering, bias-variance tradeoff etc). In the future, we plan to improve the transcription accuracy to almost 100% using [prompting as described here](https://platform.openai.com/docs/guides/speech-to-text/prompting).

The recorded audio files are stored on the server, though each audio input is overwritten by the next one to save disk space. For e.g. if an interview length is 20 question-response pairs, only one audio file will be created on the server (instead of 20). The transcribed text is stored in an AWS database, and hence all conversations are retrievable.


## Asking Questions 
This is the core functionality of the application – the Assistant tries to simulate a long conversation with the user, ask questions in a flow, and provide cues and direction when the user needs them. 

Since ChatGPT is really good at making chats (no surprises here 🙂), all we need to do is:
* Provide prompts / directions to guide the behavior of ChatGPT
* Store and provide the entire chat history as input (so it can process the next response in the context of the entire chat). 

This is done via the `ChatCompletion()` API of ChatGPT as shown below. We store the chat history in a dictionary-like object named `messages`, which is a list of responses from the `assistant` and the `user` (i.e. conversation history). To provide the context and guide the behavior of the assistant, we provide some instructions to the `system` variable.


```Python
# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai

openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "You are an interviewer who is evaluating candidates for roles such as Data Scientist, ...."},
        {"role": "user", "content": "Hello! I am excited to be in this interview."},
        {"role": "assistant", "content": "Great to see you! Let's start with the first question..."},
        {"role": "user", "content": "Regression is a technqiue used to ...."}
    ]
)
```
This returns the Assistant's response (the next interview question / hint etc) which we show to the user and wait for their response. The assistant and the user's responses are appended to `messages` to generate the next response and the coversation continues in this manner.

In real-world applications, the `system` instruction can be made as complex as required. For example, to simulate a data science mock interview, a `system` [message such as this one](https://github.com/kshitijjain91/GPT_Mock_Interview_upGrad/blob/main/data_scientist/system_message.txt) can be provided. In the hyperlinked system message, in addition to instructions such as *never reveal the right answer*, *provide hints* etc, we even provide some sample interview questions to guide the assistant's behavior.

This is an example of using a popular prompting technique called **few shot prompting** where we provide some examples to adapt the model to perform a task with limited data. You can refer to this [detailed prompting guide](https://github.com/openai/openai-cookbook/blob/main/techniques_to_improve_reliability.md) -- this guide explains the insighst from various research studies done on effective prompting techniques for various kind of tasks. 

## Providing Score and Feedback
At the end of the interview, the app provides a score and feedback on each of the user's responses. 

The app performs the grading and feedback operations via the `Completion()` API -- see [documentation here](https://platform.openai.com/docs/api-reference/completions). Unlike the `ChatCompletion()` API used above, the `Completion()` API does not need the full conversation history. It only needs one **prompt** as an input and generates one output. In our mock interview app, a simple prompt input may look something like *"Here is a question I asked the user in the interview, here is their response <response>. Use this evaluation rubric <rubric>, evaluate this response and provide a grade and feedback comments."* The output returned by the API is a numeric grade and a feedback comment. 

In reality, we provide the Assistant with a complex **evaluation rubric / prompt** which consists of detailed guiding principles on how to evaluate a response for a given question, how to award scores, etc. You can see a [sample evaluation rubric here](https://github.com/kshitijjain91/GPT_Mock_Interview_upGrad/blob/main/data_scientist/evaluation_rubric.txt). 

The `Completion()` API uses the following inputs:

```Python
chat_response = openai.Completion.create(
    engine="text-davinci-002", 
    prompt=prompt,
    max_tokens=200,
    temperature=0.5,
    n=1,
    stop=None,
    frequency_penalty=0,
    presence_penalty=0)
```
We use the `text-davinci-002` model of ChatGPT, which is one of the largest LLM models by OpenAI as of now (in terms of parameter size), but one could use `gpt-3.5-turbo' or other variants as well. On the day of writing this GPT-4 API was launched (which has much better performance), but had a waitlist to access. `max-tokens` determines the max length (num of tokens) of response generated by the API. In this case, 200 tokens (~140 words) is sufficient for grade and feedback. The details of other inputs can be found in the documentation. 

## Future Development Course of the Application
To develop and improve the app in the future, we are assessing and prioritizingf the following features:
1. **Introducing a face and voice** for the interview assistant. Hopefully, this will help the application feel more "real" to users. There are APIs available which help developers provide a face and voice to their AI chatbots, [example here](https://www.d-id.com/api/). 
2. **Fine tuning**: [Fine-tuning](https://platform.openai.com/docs/guides/fine-tuning) lets developers customize their models by training a ChatGPT model using training examples. As more users use the app, we collect data of question-response pairs, scoring and feedback etc. We can create "training datasets" by removing the bad/inaccurate responses by the Assistant and retaining the good ones (and even adding ideal responses manually). The dataset can be used to train or fine-tune a version of any model (such as `text-davinci-002`) and named, say, `upGrad_da-vinci_interview_assistant_v1`. We can keep training this with more data and create v2, v3 and so on.
3. **Adaptive tutoring:** This is not a new feature but a different app itself. With time, once we get suffience confidence on the accuracy of the assistant's responses, we intend to create a tutor app for teaching, for e.g. Data Structures and Algorithms. While learning a complex topic such as Algorithms, many learners lag behind the pace of the class/instructor or are embarrased to ask 'easy/silly' questions. An AI tutor can tailor pace of instruction, types and number of questions, cues and hints, and thus "coach the learner". An example of a very simple adaptiuve tutor app is [here](https://twitter.com/replit/status/1634298303469744136?s=48&t=lBqmTD5w6b8HmbQcfHylrg). A tutor that can tecah Algorithms will require a lot more instructional design, use of advanced prompting techniques etc.

## Cost
The models `text-davinci-002` and `gpt-3.5-turbo` cost, respectively, $0.02 and $0.002 (per 1k tokens). In an interview, each question-response pair consists of 5-6 sentences + grading and feedback (120-140 tokens). In an interview with say 20 question-response pairs, we use 140 x 20 = ~2800 tokens. If we use `text-davinci-002` for `Completion()` and `gpt-3.5-turbo` for `ChatCompletion()`, we incur approx (1400*$0.02 + 1400*$0.002)/1k = $0.03 = INR 2.5 per interview.














