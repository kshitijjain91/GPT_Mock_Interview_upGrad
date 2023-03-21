import openai
openai.api_key = "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"

prompt = "Hello, how are you today?"
model = "text-davinci-002"
chat_response = openai.Completion.create(
    engine=model,
    prompt=prompt,
    max_tokens=60,
    temperature=0.5,
    n=1,
    stop=None,
    frequency_penalty=0,
    presence_penalty=0
)
message = chat_response.choices[0].text.strip()
print(message)

