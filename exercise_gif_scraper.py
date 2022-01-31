import requests
from bs4 import BeautifulSoup

master_url = r"https://www.nickhallbodytransformations.com/exercise-demonstrations/"


def save_html(html, path):
    with open(path, "wb") as f:
        f.write(html)


header = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"
}
resp = requests.get(master_url, headers=header)

soup = BeautifulSoup(resp.text, "html.parser")

all_imgs = soup.find_all("img")
all_gifs = []

for img in all_imgs:
    if img["src"].split(".")[-1] == "gif":
        all_gifs.append(img["src"])


def get_raw_title(full_link):
    return full_link.split("/")[-1]


print(len(all_gifs))
print(all_gifs[0])

for gif in all_gifs:
    with open(f"./exercise_gifs/{get_raw_title(gif)}", "wb+") as f:
        gif_resp = requests.get(gif, headers=header)
        gif_content = gif_resp.content
        print(gif_resp.status_code)
        f.write(gif_content)
