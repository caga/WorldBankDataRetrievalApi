#!venv/bin/python3

import requests
from bs4 import BeautifulSoup
import csv

url="disisleriMainpageSource.html"
page=open(url)
soup = BeautifulSoup(page.read(),'html.parser')

#url2="MissionDetail.html"
#page2=open(url2)
#soup2 = BeautifulSoup(page2.read(),'html.parser')

#countriesRaw = soup.find_all('li', {'class':'gridder-list dp-item'})
#countryRaw=countriesRaw[0]
#countryNameRaw=countryRaw.find_all('span')[1].text
#country=countryNameRaw.replace('\n','').replace(' ','')
#countryQueryString=countryRaw['data-griddercontent']
#countryId=countryQueryString.split('?')[1].split('=')[1]

#countriesAndIds=[]
#for countryRaw in countriesRaw:
#    itemPair={}
#    countryNameRaw = countryRaw.find_all('span')[1].text
#    print(countryNameRaw)
#    country = countryNameRaw.replace('\n','').replace(' ','')
#    countryQueryString = countryRaw['data-griddercontent']
#    countryId=countryQueryString.split('?')[1].split('=')[1]
#    itemPair[country] = countryId
#    countriesAndIds.append(itemPair)
#    print(countriesAndIds)

def CountriesAndIds():
    url="disisleriMainpageSource.html"
    page=open(url)
    soup = BeautifulSoup(page.read(),'html.parser')
    countriesRaw = soup.find_all('li', {'class':'gridder-list dp-item'})
    countriesAndIds={}
    for countryRaw in countriesRaw:
        countryNameRaw = countryRaw.find_all('span')[1].text
        country = countryNameRaw.replace('\n','').replace(' ','')
        countryQueryString = countryRaw['data-griddercontent']
        countryId=countryQueryString.split('?')[1].split('=')[1]
        countriesAndIds[country] = countryId

    return countriesAndIds

countriesAndIds=CountriesAndIds()

# curl https://cd.mfa.gov.tr/mission/MissionDetail?CountryId=150174
def SingleStaticEmbassyParse():
    url="MissionDetail.html"
    page=open(url)
    soup = BeautifulSoup(page.read(),'html.parser')
    embassy = soup.find('div', {'id':'embassy'})
    ambassador = embassy.i.strong.text
    email = embassy.a.text
    return ambassador, email

def getEmbassyInfo(countryId):
    url=f"https://cd.mfa.gov.tr/mission/MissionDetail?CountryId={countryId}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'html.parser')
    country = soup.find('span', {'class':'dp-name'}).text
    print(country)
    embassy = soup.find('div', {'id':'embassy'})
    ambassador = None
    email = None
    try:
        ambassador = embassy.i.strong.text
    except:
        pass
    try:
        email = embassy.a.text
    except: 
        pass
    returnDictionary={
            'Ülke':f"{country}",
            'Büyükelçi':f"{ambassador}",
            'Email':f"{email}"
            }
    return returnDictionary
def getAllEmbassyInfo():
    EmbassyInfos=[]
    for country in countriesAndIds:
        countryId = countriesAndIds[country]
        EmbassyInfos.append(getEmbassyInfo(countryId))
    return EmbassyInfos

def cvsWriter(listofdictionaries,filename):
    with open(filename,"w") as outfile:
        fieldnames = ['Ülke','Büyükelçi','Email']
        writer=csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(listofdictionaries)
    return f"data is written in file {filename}"

def main():
    embassies = getAllEmbassyInfo()
    filename = "embassies.csv"
    cvsWriter(embassies,filename)


if __name__=="__main__":
    main()
