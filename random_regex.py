import re

some_string = '''
Grade: 7
Feedback: The response is technically correct, however it does not explain the central ideas deeply enough to demonstrate professional level expertise.
'''
# write a function that takes a string and returns a dict
def string_to_dict(some_string):
    # use regex to get the key and value
    key = re.findall(r'(?<=Grade: )\d+', some_string)[0]
    value = re.findall(r'(?<=Feedback: ).+', some_string)[0]
    # create a dict
    some_dict = {"grade": key, "feedback": value}
    return some_dict
    
    

# test the function
print(string_to_dict(some_string))
