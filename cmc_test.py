import requests

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.47"
}

session = requests.Session()
r1 = session.get("https://cmcqa.futuredial.com/")
csrftoken = session.cookies['csrftoken']

login_data=dict(
    username='username',
    password='password',
    csrfmiddlewaretoken=csrftoken,
    next='/')

r2 = session.post(r1.url, data=login_data, headers=dict(Referer=r1.url))


r3 = session.get("https://cmcqa.futuredial.com/accounts/logout/")
print(r3)
