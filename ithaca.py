
import requests
from bs4 import BeautifulSoup
import csv

from datetime import date

today = date.today()


URL = 'https://tompkinscountyny.gov/health'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')


stats = soup.find_all("td", class_="nbr")

print("current positive cases: " +
      str(int(stats[2].text) - int(stats[4].text)))

print("pending tests: " + stats[1].text.strip())



with open("cases.txt", "a") as f:
    f.write(str({str(today): {
        "current_positive": int(stats[2].text) - int(stats[4].text),
        "current_pending_tests": int(stats[1].text.strip())
        }
        }) + ",\n")

with open('cases.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    #writer.writerow(["Date", "Current_Positive_Cases", "Cumulative_Positive_Cases",  "Total_Recoverd", "Pending_Tests"])

    writer.writerow([str(today), int(stats[2].text) - int(stats[4].text) , int(stats[2].text), int(stats[4].text), int(stats[1].text.strip())])
