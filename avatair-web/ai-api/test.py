import requests
import re

# data = {
#     "iterations": 4,
#     "size": 6,
#     "prompt": "hello"
# }

# print(requests.get("http://127.0.0.1:3333").json)

# print(requests.post("http://127.0.0.1:3333", json=data).json())

# print(requests.post("http://127.0.0.1:3333", json={
#     "variables": ["age", "hair_color"]
# }).json())


# print(requests.post("http://127.0.0.1:3333/survey/?user_id=user1234", json={
#                         "values": {
#                             "nose": ["small", "medium", "large"],
#                             "haircolor": ["green", "red", "blue", "yellow"],
#                             "age": "10-20",
#                         },
#                         "ratings": [0.5, 0.3, 0.2, 0.9],
#                         "string_list": [
#                             "A person in front of a grey background with a",
#                             "@nose",
#                             " nose with ",
#                             "@haircolor",
#                             " haircolor which is ",
#                             "@age",
#                             " years old.",
#                         ],
#                     }).json())

# keys = ["nose", "age", "haircolor"]
# string = "A person in front of a grey background with a @nose nose with @haircolor haircolor which is @age years old"
# for key in keys:
#     pattern = r'@' + re.escape(key)
#     string = re.sub(pattern, "test", string)
# print(string)

from datetime import datetime, timedelta

start = datetime.now()
delta = timedelta(minutes=5)

print(start > (start + delta))