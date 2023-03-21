import openai
import re
import gradio as gr

openai.api_key = open("api_key.txt", "r").read().strip()

# Heading and instructions
heading_one = "# GPT Interview Assistant by upGrad"
heading_two = "## Linear Regression Mock Interview"

# initialize some content for system, user and assistant
system_message = '''You are a Data Science expert conducting technical interviews of candidates for roles such as professional 
Data Scientist, Machine Learning Engineer, Data Analyst etc. As the assistant, you ask interview questions to the candidate, 
evaluate the candidate's response, and ask a follow-up question. You *never* reveal the right answer to the user, you only ask follow-up questions wherever the user makes an error. 
Else, you ask further questions. Ask specific questions. If required, provide a format or attributes of an ideal answer.
'''

assistant_first_message = '''
> Hello and welcome to the mock interview on linear regression! Please answer the questions as if you are in a real job interview. I will evaluate your response and ask follow-up questions. 
I will not reveal the right answers to you, but I will guide you in the right direction if you make a mistake. Few important instructions:
> - Please answer the questions as if you are in a real job interview. Be detailed and specific. Provide examples and explanations wherever possible.
> - Type your answers in the "Your response" textbox and press Shift+Enter to submit.
> - You can end the interview at any time by clicking the "End interview and show feedback" button. You will be shown your final score and feedback.
> - To restart a new interview, refresh the page.


> **Let's start with the first question: Can you describe at least two example business problems where linear regression can be used?** 
'''

# gets a chat response from the API given a user input and message history
def getchat(message_history=None):
	connection_error = False
	try:
		reply_content = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=message_history).choices[0].message.content 
	except openai.error.APIConnectionError as e:
		connection_error = e
		reply_content = "I'm sorry, I'm having trouble connecting to the server. Please try again later."

	reply_content = reply_content.replace("\n\n", "\n")
	return reply_content, connection_error


# grade the user's response to a question according to an evaluation rubric
def grade_response(question, user_input):
	"""
	Takes an interview question, a user response, optionally an evaluation rubric as input. Evaluates the response and 
	returns a 1-10 grade and feedback as a dict e.g. {grade: 10, feedback: "Great answer!"}
	"""

	# Read the rubrics used by grade_response()
	with open('eval_rubric.txt') as f:
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

# run only if directly executed on terminal
if __name__ == "__main__":

	with gr.Blocks(theme=gr.themes.Soft()) as demo:
		message_history = gr.State([
			{"role": "system", "content": system_message}, 
			{"role": "assistant", "content": assistant_first_message}])
		scores = gr.State([]) # store question, response, grades, feedback in a list of dicts [{question}, {response}, {grade}, {feedback}]
		gr.Markdown(heading_one) # show the heading and instructions
		gr.Markdown(heading_two)
		gr.Markdown(assistant_first_message)

		chatbot = gr.Chatbot(lines=4, label="Interview Assistant")
		msg = gr.Textbox(lines=4, label="Your response", placeholder="Type here & press Shift+Enter to submit")
		some_line = gr.Markdown("##")
		horizontal_line_one = gr.Markdown("____")
		score_output = gr.Markdown("> ## Your Final Score Will Appear Here: ")
		feedback_output = gr.Markdown("> ## Your Feedback Will Appear Here: ")
		another_line = gr.Markdown("##")
		horizontal_line_two = gr.Markdown("____")
		show_feedback = gr.Button("End interview and show feedback")

		def user(user_message, gr_chat_history, message_history, scores):
			return "", gr_chat_history + [[user_message, None]], message_history, scores
			
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
			# calculate total score
			try:
				total_score = sum([int(score["score"]) for score in scores if score["score"] is not None]) / (10*len([score["score"] for score in scores if score["score"] is not None]))
			except ZeroDivisionError:
				total_score = "> ## Your score is 0%."
				feedback_string = "> ## No feedback yet. Please type at least one response to see."
				return total_score, feedback_string, None

			total_score = "> ## Your score is " + str(round(total_score*100, 1)) + "%." # convert to percentage
			# create a string of question, response, score, feedback
			feedback_string = '''> ## Feedback on your responses:''' + '''\n\n'''
			for score in scores[1:]: # skip the first score (the assistant's first message)
				feedback_string += '''\n\n**Question:** {0}'''.format(score["question"])
				feedback_string += '''\n\n**Your response:** {0}'''.format(score["response"].capitalize())
				feedback_string += '''\n\n**Score:** {0}'''.format(score["score"])
				feedback_string += '''\n\n**Feedback:** {0}'''.format(score["feedback"] if score["feedback"] is not None else "No feedback.")
				feedback_string += '''\n\n---\n\n'''
			return total_score, feedback_string, None
		
		msg.submit(user, 
	     [msg, chatbot, message_history, scores], 
		 [msg, chatbot, message_history, scores], 
		 queue=False).then(bot, 
		     [chatbot, message_history, scores], 
			 [chatbot, message_history, scores]
		)
		
		show_feedback.click(show_feedback_fn,
			inputs=scores,
			outputs=[score_output, feedback_output, chatbot],
			queue=False)
		
	demo.launch(share=True)