# random input tester

print('''This is a small input test program. Enter "exit" (without the quotes) to exit''')

user_input = ""

while user_input != "exit":
	user_input = input(">")
	print("your input was {}".format(user_input))


