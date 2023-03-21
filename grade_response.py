import openai
import re

openai.api_key = "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"

# evaluation_rubric
with open('eval_rubric.txt') as f:
	eval_rubric = ' '.join(f.readlines())

print(eval_rubric)

def grade_response(question, user_input, eval_rubric=eval_rubric):
	"""
	takes in an interview question, a user response, optionally an evaluation rubric. Evaluates the response and returns a 1-10 grade and constructive feedback. 
	"""

	prompt = eval_rubric + "\n" + "Question: {0}".format(question) + "\n" + "User response: {0}".format(user_input)
	model = "text-davinci-002"

	chat_response = openai.Completion.create(
    engine=model,
    prompt=prompt,
    max_tokens=200,
    temperature=0.5,
    n=1,
    stop=None,
    frequency_penalty=0,
    presence_penalty=0)

	message = chat_response.choices[0].text.strip()

	return(message)



 # random testing
question = """That's correct. Now, can you explain the difference between simple linear regression and multiple linear regression?"""
user_input = """Simple linear regression is used to predict output using only a single variable, which multiple regression is used to predict the target variable from multiple independent variables."""

grade = grade_response(question, user_input, eval_rubric)
print(grade)













