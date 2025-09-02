#!venv/bin/python3

import requests
from bs4 import BeautifulSoup
import csv

def cvsWriter(listofdictionaries,filename):
    with open(filename,"w") as outfile:
        fieldnames = ['Organizasyon','Email']
        writer=csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(listofdictionaries)
    return f"data is written in file {filename}"

def main():
    url="internationalOrganizations.html"
    page=open(url)
    soup = BeautifulSoup(page.read(),'html.parser')

    Organizations = soup.find_all('li')

    ListOfOrganizations = []
    for organization in Organizations:
        name = "Yok"
        email = "Yok"
        links = organization.find_all('a')
        try:
            name = links[0].text.replace('\n','').strip()
        except:
            pass
        try:
            email = links[1].text
        except:
            pass
        dictionary = { 'Organizasyon': name,
                      'Email':email
                      }
        ListOfOrganizations.append(dictionary)
    return cvsWriter(ListOfOrganizations,'organizations.csv')

if __name__=="__main__":
    main()
