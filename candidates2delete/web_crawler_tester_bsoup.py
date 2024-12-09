import requests
from bs4 import BeautifulSoup

url = "https://www.whoscored.com/"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

title = soup.title.text  # Access the <title> element's text content
print(title)

links = [a.get("href") for a in soup.find_all("a")]
print(links)
