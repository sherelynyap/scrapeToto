from selenium import webdriver
from bs4 import BeautifulSoup
import sqlite3
import platform
import re
from webdriver_manager.chrome import ChromeDriverManager
import requests
from tqdm import tqdm


# connect to database
conn = sqlite3.connect('toto.sqlite')
cur = conn.cursor()

url = 'https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx'
browser = webdriver.Chrome(ChromeDriverManager().install())
# browser = webdriver.Chrome()
browser.get(url)
html_source = browser.page_source
browser.quit()
soup = BeautifulSoup(html_source, 'html.parser')
drawlist = []
for drawDate in soup.select_one('.form-control.selectDrawList').findChildren():
    drawlist.append(drawDate['querystring'])

print("Inserting winning numbers into database...")
for draw in tqdm(drawlist,ascii=False, ncols=100):
    url = 'https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx?'+draw
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    numbers = [int(element.text) for element in soup.find_all('td', {'class': re.compile(r'^win')})]
    date = soup.find('th', {'class': re.compile(r'drawDate')}).text.split(', ')
    day = date[0]
    date1 = date[1]
    
    for i in numbers:
        cur.execute(f"INSERT OR IGNORE INTO date(draw_no,day,date) VALUES(?,?,?)",(i, day, date1))
    conn.commit()

