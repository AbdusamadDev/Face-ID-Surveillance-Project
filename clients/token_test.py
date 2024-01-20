import requests

print(
    requests.get(
        f"http://fakeserver.pythonanywhere.com/auth/token/",
    ).content
)
