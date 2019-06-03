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

# Creates a table of definitions
definitions = soup.find_all('p', class_='Definition')

for item in definitions:
    dfn = [item.find(text=True, recursive=False)]
    for subItem in item.find_all():
        if subItem.name == 'dfn':
            term = subItem.get_text() #The term that will be defined
