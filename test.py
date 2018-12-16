import requests
from bs4 import BeautifulSoup

r = requests.get("http://aclweb.org/anthology/P18-2015")
with open("downloads/test.pdf", "wb") as f:
    f.write(r.content)