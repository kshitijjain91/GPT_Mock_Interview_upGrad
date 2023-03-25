import openai
import re
import gradio as gr
from pydub import AudioSegment

openai.api_key = open("api_key.txt", "r").read().strip()

interview_directory = "data_scientist"

# Heading and instructions
heading_one = '''# <span style="color:gray">GPT Interview Assistant by </span><span style="color:firebrick">upGrad</span>'''

rubric_filepath = interview_directory + "/evaluation_rubric.txt"
system_message_filepath = interview_directory + "/system_message.txt"
assistant_first_message_filepath = interview_directory + "/assistant_first_message.txt"
		
with open(system_message_filepath) as f:
	system_message = ' '.join(f.readlines())

with open(assistant_first_message_filepath) as f:
	assistant_first_message = ' '.join(f.readlines())

def getchat(message_history=None):
	"""
	gets a chat response from the API given a user input and message history
	"""
	connection_error = False
	try:
		reply_content = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=message_history).choices[0].message.content 
	except openai.error.APIConnectionError as e:
		connection_error = e
		reply_content = "I'm sorry, I'm having trouble connecting to the server. Please try again later."

	reply_content = reply_content.replace("\n\n", "\n")
	return reply_content, connection_error


def grade_response(question, user_input):
	"""
	Takes an interview question and a user response. Evaluates the response using an evaluation rubric and 
	returns a 1-10 grade and feedback as a dict e.g. {grade: 10, feedback: "Great answer!"}
	"""

	# Read the rubrics used by grade_response()
	with open(rubric_filepath) as f:
		eval_rubric = ' '.join(f.readlines())

	prompt = eval_rubric + "\n" + "Question: {0}".format(question) + "\n" + "User response: {0}".format(user_input)
	model = "text-davinci-002"

	# get the grade and feedback from ChatGPT API
	connection_error = False
	try:
		chat_response = openai.Completion.create(engine=model, 
					   prompt=prompt,
					   max_tokens=200,
					   temperature=0.5,
					   n=1,
					   stop=None,
					   frequency_penalty=0,
					   presence_penalty=0)
	except openai.error.APIConnectionError as e:
		connection_error = e
		message = "I'm sorry, I'm having trouble connecting to the server. Please try again later."

	message = chat_response.choices[0].text.strip()
	
	# convert to lowercase
	message = message.lower()
	# remove single quotes from the string
	message = message.replace("'", "")
	# remove double quotes from the string
	message = message.replace('"', '')

	# use regex to get the key and value
	try:
		grade = re.findall(r'(?<=grade: )\d+', message)[0]
	except IndexError:
		grade = None
	
	try:
		feedback = re.findall(r'(?<=feedback: ).+', message)[0]
		feedback = feedback.replace('"', '')
		feedback = feedback.replace("}", "")
		feedback = feedback.replace("{", "")
		feedback = feedback.replace('\n\n', '\n')	
	except IndexError:
		feedback = None
		feedback = "No feedback provided for this response."

	# write grade and feedback to a text file
	with open('scores.txt', 'a') as f:
		f.write(message)
		f.write("\n")
		f.write("grade={0}".format(grade))
		f.write("\n")
		f.write("feedback={0}".format(feedback))
		f.write("\n\n")
		
	message = {"grade": grade, "feedback": feedback}
	return message, connection_error

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

max_rows = 30 # max number of rows to show in feedback table

with gr.Blocks(theme=gr.themes.Default(font=[gr.themes.GoogleFont("Inter"), "Arial", "sans-serif"])) as demo:
	message_history = gr.State([
		{"role": "system", "content": system_message}, 
		{"role": "assistant", "content": assistant_first_message}])
	scores = gr.State([]) # store question, response, grades, feedback in a list of dicts [{question}, {response}, {grade}, {feedback}]
	gr.Markdown(heading_one) # show the heading and instructions
	line_below_heading = gr.Markdown("____")
	gr.Markdown(assistant_first_message)
	chatbot = gr.Chatbot(lines=4, label="Interview Assistant")
	with gr.Row():
		audio_input = gr.Audio(source="microphone", type="filepath")
		transcribe_button = gr.Button("Transcribe")
	msg = gr.Textbox(lines=4, label="Your response", placeholder="Record from mic, transcribe and press Shift+Enter to submit.")
	some_line = gr.Markdown("##")
	horizontal_line_one = gr.Markdown("____")
	show_feedback = gr.Button("End Interview and See Score & Feedback")
	horizontal_line_two = gr.Markdown("____")

	
	another_line = gr.Markdown("##")
	
	feedback_array = []
	score_number = gr.Textbox(label="% Score", visible=False)
	
	for n in range(max_rows):
		with gr.Row() as output_row:
			question_column = gr.Textbox(label="Question", visible=False)
			response_column = gr.Textbox(label="Your response", visible=False)
			score_column = gr.Textbox(label="Score", visible=False)
			feedback_column = gr.Textbox(label="Feedback", visible=False)
			feedback_array.append(question_column)
			feedback_array.append(response_column)
			feedback_array.append(score_column)
			feedback_array.append(feedback_column)
	
	feedback_array.append(score_number) # the last element of feedback array is the score number
	

	def user(user_message, gr_chat_history, message_history, scores):
		return "", gr_chat_history + [[user_message, None]], message_history, scores, None
		
	def bot(gr_chat_history, message_history, scores):
		last_user_message = gr_chat_history[-1][0] # get the last user message
		last_question = message_history[-1]["content"] # question asked by the assistant (for grading)
		message_history.append({"role": "user", "content": last_user_message})
		# grade the user's response
		score_and_feedback, connection_error_grade = grade_response(question=last_question, user_input=last_user_message)
		if connection_error_grade:
			raise gr.Error("API connection error! Refresh page to restart.")
		
		scores.append({"question": last_question, "response": last_user_message, "score": score_and_feedback["grade"], "feedback": score_and_feedback["feedback"]})	
		# get chat response from ChatCompletion API
		reply_content, connection_error_chat = getchat(message_history=message_history)
		if connection_error_chat:
			raise gr.Error("API connection error! Refresh page to restart.")
		message_history.append({"role": "assistant", "content": reply_content})
		gr_chat_history[-1][1] = reply_content.replace(">", "")
		return gr_chat_history, message_history, scores
	
	
	def show_feedback_fn(scores):
		if len(scores) > max_rows:
			scores = scores[1:(max_rows+1)]
		else:
			scores = scores[1:]

		for i, score in enumerate(scores): 
			feedback_array[i*4] = gr.update(value=score["question"], visible=True)
			feedback_array[i*4+1] = gr.update(value=score["response"], visible=True)
			feedback_array[i*4+2] = gr.update(value=score["score"], visible=True)
			feedback_array[i*4+3] = gr.update(value=score["feedback"], visible=True)

		try:
			score_number = sum([int(score["score"]) for score in scores if score["score"] is not None]) / (10*len([score["score"] for score in scores if score["score"] is not None]))
			score_number = round(score_number*100, 1)
		except ZeroDivisionError:
			score_number = 0
		
		score_number = str(score_number) + "%"
		feedback_array[-1] = gr.update(value=score_number, visible=True) # the last element of feedback array is the score number

		return feedback_array 

	msg.submit(user, 
		[msg, chatbot, message_history, scores], 
		[msg, chatbot, message_history, scores, audio_input], 
		queue=False).then(bot, 
			[chatbot, message_history, scores], 
			[chatbot, message_history, scores])
	
	transcribe_button.click(whisper_transcribe, audio_input, msg)
	
	show_feedback.click(show_feedback_fn,
		inputs=scores,
		outputs=feedback_array)
		
# run only if directly executed on terminal
if __name__ == "__main__":
	demo.launch(share=False)