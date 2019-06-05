# What we know
# <h1>: Title of the regulation
# <h2>: Parts and Schedules
# <h3>: Divisions
# <h4>: Subdivision
# <h5>: Category or sub-sub division, these don't seem to have numbers
# <class="sectionLabel">: Sections, these are in the format [#]
# <class="lawlabel">: Sub-sections, sub-sub sections etc. In the format (#) -> (Char) -> (roman numeral)
# To scrape this page into a data set I am going to create two data sets.
#   1. Make an indexed list of all headings
#   2. Make a list of sections -> sub.... sections with a key field indicating their hierarchy IE:
#       Title | Part | Division | Subdivision | Category |  Section | Sub-section | SS Section | SSS Section
#       *This will make scraping easier to use this format, however, the final data set itself may be adjusted into
#        a more use-able format.

# --- provision lists <ul> ---------
# 1. Direct descendants will always be one or more lists <li> without a class
# 2. <li> descendants will either be <p> or another <ul> for most cases, <div> and <figure> show-up in low frequency
#   a. if descendant = <p> then they will have one of the following classes
#       Subsection
#       MarginalNote
#       Paragraph
#       Sub paragraph
#       Clause
#       caption *Will probably exclude the classes below this
#       Footnote
#       Paragraph
#
#   b. if descendant = <ul>, recursively process

from bs4 import BeautifulSoup
import regsWithLegsFunctions as udf
import pandas as pd
import requests

# Stores a list heading tag types to take into consideration adn the corresponding level
headingDict = {
    "h2": 1,
    "h3": 2,
    "h4": 3,
    "h5": 4}

page = requests.get("https://laws-lois.justice.gc.ca/eng/regulations/SOR-2018-108/FullText.html")  # Retrieve regulations html document
soup = BeautifulSoup(page.content, 'html.parser')  # Creates beautiful soup objects

# Initializes a pandas data frame for heading data
titleOfAct = soup.find(class_="Title-of-Act").get_text()
subText = soup.find(class_='ChapterNumber').get_text()
tocFrame = pd.DataFrame([[0, "Title of Regulation", titleOfAct, subText, '']])  # Creates first entry

# Drill down to the relevant part of the HTML code
mainBody = soup.find(id='docCont').find('div')  # returns all elements from the page
subPart = mainBody.find_all('section', recursive=False)

intro = subPart[0]  # Stores introduction text
regPart = subPart[1]  # Stores regulation text

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

#### FOR FUTURE USE
# # Append data frame with new row
# tocFrame = tocFrame.append([[headingLevel,
#                              headingType,
#                              headingText,
#                              headingDescription,
#                              headingID]],
#                            ignore_index=True)
# # Renames column names for readability
# tocFrame = tocFrame.rename(index=str, columns={0: "headingLevel",
#                                                1: "headingType",
#                                                2: 'headingText',
#                                                3: 'headingDescription',
#                                                4: 'headingID'})