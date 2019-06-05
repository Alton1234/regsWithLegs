from bs4 import BeautifulSoup
import regsWithLegsFunctions as udf
import pandas as pd
import requests
page = requests.get("https://laws-lois.justice.gc.ca/eng/regulations/SOR-2018-108/FullText.html")

# Stores a list heading tag types to take into consideration adn the corresponding level
headingDict = {
    "h2": 1,
    "h3": 2,
    "h4": 3,
    "h5": 4}

soup = BeautifulSoup(page.content, 'html.parser')
# Drill down to the relevant part of the HTML code
mainBody = soup.find(id='docCont').find('div')  # returns all elements from the page
subPart = mainBody.find_all('section', recursive=False)
intro = subPart[0]  # Stores introduction text
regPart = subPart[1]  # Stores regulation text
i = 1
for item in regPart.find_all(recursive=False):
    # Checks if tag is a heading
    if item.name in headingDict:
        varList = udf.proc_heading(item, headingDict[item.name])
    # processes classes
    elif len(item.attrs) > 0:
        # Marginal notes, these exist
        if item.get('class')[0] == 'MarginalNote':
            varList = udf.proc_marginalnote(item, 5)
        # Retrieves sections
        elif item.get('class')[0] == 'Section':
            varList = udf.proc_section(item, 6)
        # Provision lists (contains sections and subsections)
        elif item.get('class')[0] == 'ProvisionList':
            tempList = udf.proc_provisions(item)
            print(*tempList, sep = "\n")
