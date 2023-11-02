import requests


url = "http://192.168.1.132:8000/api/criminals/125/"
context = {
    "image": open("main.jpg", "rb").read(),
}

request = requests.patch(url, data=context)
print(request.status_code)
print(request.content)
