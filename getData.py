#!venv/bin/python3

import json
import requests
import sys
import datetime as dt
from py_markdown_table.markdown_table import markdown_table as md_table
import os

indicatorData=[]
countryData={}
mdReportsDirectory = "IndicatorReports/mdReports"
docReportsDirectory = "IndicatorReports/docReports"
indicatorCodesWB = {
        'Nüfus' : 'SP.POP.TOTL',
        'GSYH ($)' : 'NY.GDP.MKTP.CD', 
        'GSYH (Kişi Başı $)': 'NY.GDP.PCAP.CD',
        'GSYH % Büyüme' : 'NY.GDP.MKTP.KD.ZG',
        'GSYH % Sanayi Payı':'NV.IND.TOTL.ZS',
        'GSYH % Hizmet Payı' : 'NV.SRV.TOTL.ZS',
        'GSYH % Tarım Payı' : 'NV.AGR.TOTL.ZS',
        'Enflasyon %' : 'FP.CPI.TOTL.ZG',
        'İşsizlik %' : 'SL.UEM.TOTL.ZS',
        'İhracatda Yük. Tek. Payı %' : 'TX.VAL.TECH.MF.ZS',
        'İhracat ($)' : 'BX.GSR.MRCH.CD',
        'İthalat ($)' : 'BM.GSR.MRCH.CD',
        'Arge/GSYH % Oranı': 'GB.XPD.RSDV.GD.ZS',
                    }

def getArguments(country:str = 'TUR'):
    try: 
       rv_country = sys.argv[1] #returned value:rv
    except:
        pass
    else:
       country=rv_country
    return country


#def ConvertMdToDocx(file:str)
#def ConvertMdToPdf(file:str):
#"pandoc -f markdown -t pdf {mdfile} -o {pdffile} --lua-filter=$HOME/.bin/pandocFilters/links-to-pdf.lua --filter $HOME/.bin/pandoc-crossref --citeproc"

#def human_format(num):
#    num = float('{:.3g}'.format(num))
#    magnitude = 0
#    while abs(num) >= 1000:
#        magnitude += 1
#        num /= 1000.0
#    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.3f%s' % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])

def GetGeneralDataFromWB(country = 'TUR'):
    api_url = f"https://api.worldbank.org/v2/countries/{country}?format=json"
    response = requests.get(api_url)
    data_meta = response.json()[0]
    data = response.json()[1][0]
    countryFullName = data['name']
    region = data['region']['value']
    incomeLevel = data['incomeLevel']['value']
    capitalCity = data['capitalCity']
    longitude = data['longitude']
    latitude = data['latitude']
    generalData = CountryData={
            'Ülke':data['name'],
            'Bölge':data['region']['value'],
            'Gelir Seviyesi':data['incomeLevel']['value'],
            'Başkent':data['capitalCity'],
#            'longitude':data['longitude'],
#            'latitude':data['latitude'],
            }
    return generalData 

def GetIndicatorValueFromWB(country:str,indicator:str):

    api_url = f"https://api.worldbank.org/v2/countries/{country}/indicator/{indicator}?format=json"
    response = requests.get(api_url)
    data_meta = response.json()[0]
    data = response.json()[1]
    indicatorName = data[0]['indicator']['value']
    countryName = data[0]['country']['value']
    indicatorValue = None
    indicatorYear = None
    for data_item in data:
        if data_item['value'] is not None:
#            indicatorValue = f"{data_item['value']:,.2f}"
            indicatorValue = human_format(float(data_item['value']))
            indicatorYear = f"{data_item['date']}"
            break
    returnValue={
#            'country':countryName,
            'indicator':indicatorName,
            'value':indicatorValue,
            'year':indicatorYear
            }
    return returnValue

def GetIndicatorsFromWB(country:str):

    data = []
    indice = 1
    totalNumber=len(indicatorCodesWB)

    prompt = f"Indicators From WorldBank for ({country}): \n"
    print(prompt)

    for indicator in indicatorCodesWB:
        indicatorWB=indicatorCodesWB[indicator]
        dataItemWB = GetIndicatorValueFromWB(country,indicatorWB)
        dataItem={}
        dataItem['Gösterge'] = indicator + f" ({dataItemWB['year']})"
        dataItem['Değer'] = dataItemWB['value']
        #dataItem['Yıl'] = dataItemWB['year']
        #printString = f"{country}-{dataItemWB['indicator']}:{dataItemWB['value']}-{dataItem['gosterge']} {dataItemWB['year']}"
        printString = f"{dataItem['Gösterge']}:{dataItem['Değer']}"
        print(printString)
        data.append(dataItem)
#        print(f"{indice} of {totalNumber} indicator(s) is gotten from WB")
        indice+=1
    return data
 
#def main(country='TUR'):
def FileHeader(gdata:dict,data:dict):
    time = dt.datetime.now()
    timestamp = time.timestamp()
    #idno = int(timestamp)
    idno = IdGenerator()
    date = time.strftime('%d/%m/%Y')
    country = gdata['Ülke']
    #bibfile = "reports/bibfiles/country.replace(' ','')+'.bib'"
    bibfile = "api.bib"
    title = f"{country} Automatic Indicator Report"
    headerString=f"""---
id: {idno}
date: {date}
author: Ülke Yönetim Sistemi
title: {title}  
n_type: indicatorReport
bibliography: {bibfile}
citation-style: ieee-with-url.csl
colorlinks: true
keywords:
modify:
--- """
    return headerString,idno

def ReportMd(gdata:dict,data:dict):
    countryName = gdata['Ülke']
    fileHeader,idno = FileHeader(gdata,data)
    filename = f"{mdReportsDirectory}/{gdata['Ülke'].replace(' ','')}_Report.md"
    gDataTableRaw = md_table([gdata]).set_params(row_sep='markdown').get_markdown()
    gDataTable = gDataTableRaw.replace('```','')
    dataTableRaw = md_table(data).set_params(row_sep='markdown').get_markdown() 
    dataTable = dataTableRaw.replace('```','')
    bodyString = f""" 
{fileHeader}

# {countryName} Otomatik Rapor Tabloları @wbapi
   


{gDataTable}
   


{dataTable}


## Kaynaklar:

    """
    with open (f"{filename}",'w') as f:
        f.write(bodyString)
    f.close()
    result=f"Report File saved as {filename}"
    return filename

def IdGenerator(): 
    time = dt.datetime.now()
    timestamp = time.timestamp()
    idno = int(timestamp)
    return idno


    

def main(country = 'TUR'):
    country=getArguments()
    data=GetIndicatorsFromWB(country)
    gdata=GetGeneralDataFromWB(country)
    reportFile=ReportMd(gdata,data)
    docxFile=f"{docReportsDirectory}/{reportFile.split('/')[-1].split('.')[0]+'.docx'}"
#    docxFile=reportFile.split('.')[0]+'.docx'
    os.system(f"pandoc -f markdown-tex_math_dollars -t docx -o {docxFile} {reportFile} --filter $HOME/.bin/pandoc-crossref --citeproc --reference-doc=custom-reference.docx")
    os.system(f"libreoffice {docxFile}")
    return 0
#    for dataItem in data:
#        printString = f"{country}-{dataItem['Gösterge']}:{dataItem['Değer']} {dataItem['Yıl']}"
#        print(printString)
    return 0

if __name__=="__main__":
   #GetAllFromWB()
   #FromWB()
   #FromWB2()
#   GetAllAvailableFromWB()
#   GetAllAvailableFromWB_bash()
    main()
