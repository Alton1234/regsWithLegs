#Notes
# In the regulations, h2 are the main headings
#
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
page = requests.get("https://laws-lois.justice.gc.ca/eng/regulations/SOR-2018-108/FullText.html")
print(page.content)

soup = BeautifulSoup(page.content, 'html.parser')
regContents = soup.find(id= 'docCont').find_all()

# Initial heading: the title of the regulations
h1 = soup.find('h1').get_text()

headingData = pd.DataFrame([['H1', h1, '', '']])

# Creates a data frame that houses the basic table of contents
# columns=['headingType', 'headingCode', 'headingText', 'parentCode']
for item in regContents:
    if item.name == 'h2':
        hSpan = list(item.find_all('span'))
        headingType = "H2"
        h2 = hSpan[0].get_text()
        parentCode = h1
        if len(hSpan) == 1:
            headingText = ''
        else:
            headingText = hSpan[1].get_text()

        hTemp = pd.DataFrame([[headingType, h2, headingText, parentCode]])
        headingData = headingData.append(hTemp, ignore_index=True)

    elif item.name == 'h3':
        hSpan = list(item.find_all('span'))
        headingType = "H3"
        h3 = hSpan[0].get_text()
        parentCode = h2
        if len(hSpan) == 1:
            headingText = ''
        else:
            headingText = hSpan[1].get_text()
        hTemp = pd.DataFrame([[headingType, h3, headingText, parentCode]])
        headingData = headingData.append(hTemp, ignore_index=True)

    elif item.name == 'h4':
        hSpan = list(item.find_all('span'))
        headingType = "H4"
        h4 = hSpan[0].get_text()
        parentCode = h3
        if len(hSpan) == 1:
            headingText = ''
        else:
            headingText = hSpan[1].get_text()
        hTemp = pd.DataFrame([[headingType, h4, headingText, parentCode]])
        headingData = headingData.append(hTemp, ignore_index=True)

    elif item.name == 'h5':
        headingType = "H5"
        h5 = item.get_text()
        parentCode = h4
        if len(hSpan) == 1:
            headingText = ''
        else:
            headingText = hSpan[1].get_text()
        hTemp = pd.DataFrame([[headingType, h5, headingText, parentCode]])

        headingData = headingData.append(hTemp, ignore_index=True)

#Creates a table of definitions
#definitions = soup.find_all('p', class_='Definition')

#Renames columns
headingData = headingData.rename(index=str, columns={0:"headingType", 1:'headingCode', 2:'headingText', 3:'parentCode'})

export_csv = headingData.to_csv (r'C:\Users\Dragonfly\Documents\export_dataframe.csv', index = None, header=True)

print(headingData)
