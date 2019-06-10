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
#
# *************** Regulation identification system *************
# Each code will be stored in a separate column
# Part.Divsision.Subdivision.Section.Subsection.Paragraph.Subparagraph.clause
# Example: 'SOR/2018-108'.1.A.1.1.a.i.A
# Coding approach:
#   Regulation code will persist for each new coded bit
#   Parts will persist until the next part
#   Divisions will persist until the next division or part, if no division will be 0
#   Subdivisions will persist until the next Subdivision or higher level heading
#   Sections will persis until the next section or higher level heading
#   etc etc.

from bs4 import BeautifulSoup
from collections import OrderedDict
import regsWithLegsFunctions as udf
import pandas as pd
import requests

# Stores a list heading tag types to take into consideration adn the corresponding level
headingDict = {
    "h2": 1,
    "h3": 2,
    "h4": 3,
    "h5": 4}

# Retrieve regulations html document
# Safe food for Canadians regulations
# page = requests.get("https://laws-lois.justice.gc.ca/eng/regulations/SOR-2018-108/FullText.html")
# regulationID = 'SOR/2018-108'

# Food and drug regulations
page = requests.get('https://laws.justice.gc.ca/eng/regulations/c.r.c.,_c._870/FullText.html')
regulationID = 'C.R.C., c. 870'  # Food and drug regulations

# Migratory birds regulations
# page = requests.get('https://laws-lois.justice.gc.ca/eng/regulations/C.R.C.,_c._1035/FullText.html')

# Yellowknife Airport zoning regulations *** This doesn't seem to work quite as well, there is loss ***
#page = requests.get('https://laws-lois.justice.gc.ca/eng/regulations/SOR-81-472/FullText.html')

soup = BeautifulSoup(page.content, 'lxml')  # Creates beautiful soup objects

# Drill down to the relevant part of the HTML code
mainBody = soup.find(id='docCont').find('div')  # returns all elements from the page
subPart = mainBody.find_all('section', recursive=False)
intro = subPart[0]  # Stores introduction text
regPart = subPart[1]  # Stores regulation text

# Key value initial assignment
keyFields = OrderedDict([
    ('REGULATION', regulationID),
    ('PART', '0'),
    ('DIVISION', '0'),
    ('SUBDIVISION', '0'),
    ('SUBDIVISION CONTEXT', '0'),
    ('SECTION CONTEXT', '0'),
    ('SECTION', '0'),
    ('SUBSECTION CONTEXT', '0'),
    ('SUBSECTION', '0'),
    ('PARAGRAPH', '0'),
    ('SUBPARAGRAPH', '0'),
    ('CLAUSE', '0')
])

# Keeps track of block levels
blockLevel = {
    'REGULATION': 0,
    'PART': 1,
    'DIVISION': 2,
    'SUBDIVISION': 3,
    'SUBDIVISION CONTEXT': 4,
    'SECTION CONTEXT': 5,
    'SECTION': 6,
    'SUBSECTION CONTEXT': 7,
    'SUBSECTION': 8,
    'PARAGRAPH': 9,
    'SUBPARAGRAPH': 10,
    'CLAUSE': 11
}

# Initializes a pandas data frame for heading data
titleOfAct = soup.find(class_="Title-of-Act").get_text()
subText = soup.find(class_='ChapterNumber').get_text()
pageData = pd.DataFrame([[0,  # Level
                          "Regulation",  # Type of regulation block
                          regulationID,  # Text/number of heading or section
                          titleOfAct,  # Description of heading/caption or section contents
                          '',  # HTML id tag, if any
                          regulationID,  # Regulation
                          '0',  # Part
                          '0',  # Division, numeric
                          '0',  # Subdivision, uppercase letter
                          '0',  # Subdivision context, auto-generated number
                          '0',  # Section context, auto-generated number
                          '0',  # Section, number
                          '0',  # Subsection context, auto-generated number
                          '0',  # Subsection, number in brackets (), simplified to show only number
                          '0',  # Paragraph, lower case letter
                          '0',  # Sub paragraph section, roman numeral
                          '0'   # clause section, upper case letter
                          ]]
                        )

# *********** Definitions ********************************
# Retrieves a list of terms and definitions from the regulations.
# These aren't "smart" for now and won't do a very good job at preserving format, however
# The text should be there

definitions = pd.DataFrame([["I am a term", "I am a definition"]])  # initial data frame
for item in soup.find_all('dd'):
    definition = ""
    for string in item.strings:
        if string.parent.name == 'dfn':
            if string.strip() == ")":
                term = "98765"
            else:
                term = string
        else:
            definition = definition + string
    if term == "98765":
        tempDF = pd.DataFrame([[term, definition]])
    else:
        tempDF = pd.DataFrame([[term, term + definition]])

    definitions = definitions.append(tempDF, ignore_index=True)

definitions = definitions.rename(index=str, columns={0: "Term", 1: "Definition"})

# ************ Process regulation bits and pieces *****************
SubdivisionContextCounter = 0
SectionContextCounter = 0
subsectionContextCounter = 0

varList = [9999]
# retrieves body and heading information
for item in regPart.find_all(recursive=False):

    # *************** Process Headings ***********************************
    if item.name in headingDict:
        if item.name == 'h5':
            SubdivisionContextCounter += 1

        varList = udf.proc_heading(item,
                                   headingDict[item.name],
                                   SubdivisionContextCounter)  # Returns cleaned list of data

        # Processes key values
        if varList[1] in keyFields:
            keyFields[varList[1]] = varList[2]  # Stores coded value

            # Reset all codes after the level of the heading
            for i, (key, value) in enumerate(keyFields.items()):
                if i > varList[0]:
                    keyFields[key] = '0'

        #Add key values to list
        for i, (key, value) in enumerate(keyFields.items()):
            varList.append(value)

        # Adds new record to data frame
        pageData = pageData.append(udf.create_dataframe(varList), ignore_index=True)

    # *************** Process tag classes ***********************************
    elif len(item.attrs) > 0:

        # *************** Process marginal notes - Section context  ***********************************
        if item.get('class')[0] == 'MarginalNote':
            SectionContextCounter += 1

            varList = udf.proc_marginalnote(item,
                                             blockLevel['SECTION CONTEXT'],
                                             'SECTION CONTEXT',
                                             SectionContextCounter)

            # Processes key values
            if varList[1] in keyFields:
                keyFields[varList[1]] = varList[2]  # Stores coded value

                # Reset all codes after the level of the heading
                for i, (key, value) in enumerate(keyFields.items()):
                    if i > varList[0]:
                        keyFields[key] = '0'

            # Add key values to list
            for i, (key, value) in enumerate(keyFields.items()):
                varList.append(value)

            # Adds new record to data frame
            pageData = pageData.append(udf.create_dataframe(varList), ignore_index=True)

        # *************** Process Sections ***********************************
        elif item.get('class')[0] == 'Section':
            varList = udf.proc_section(item, blockLevel['SECTION'])

            # Processes key values
            if varList[1] in keyFields:
                keyFields[varList[1]] = varList[2]  # Stores coded value

                # Reset all codes after the level of the heading
                for i, (key, value) in enumerate(keyFields.items()):
                    if i > varList[0]:
                        keyFields[key] = '0'

            # Add key values to list
            for i, (key, value) in enumerate(keyFields.items()):
                varList.append(value)

            # Adds new record to data frame
            pageData = pageData.append(udf.create_dataframe(varList), ignore_index=True)

        # *************** Process provision lists  ***********************************
        elif item.get('class')[0] == 'ProvisionList':
            tempList = udf.proc_provisions(item, subsectionContextCounter)  # Returns a list of page elements

            for varList in tempList:

                if varList[1] == 'SUBSECTION CONTEXT':
                    subsectionContextCounter = int(varList[2])
                # Processes key values
                if varList[1] in keyFields:
                    keyFields[varList[1]] = varList[2]  # Stores coded value

                    # Reset all codes after the level of the heading
                    for i, (key, value) in enumerate(keyFields.items()):
                        if i > varList[0]:
                            keyFields[key] = '0'

                # Add key values to list
                for i, (key, value) in enumerate(keyFields.items()):
                    varList.append(value)

                # Adds new record to data frame
                pageData = pageData.append(udf.create_dataframe(varList), ignore_index=True)


# Force string format on code field
for i in range(16):
    pageData[i] = pageData[i].astype(str)


# Rename pages
pageData = pageData.rename(index=str, columns={0: "headingLevel",
                                               1: "headingType",
                                               2: 'headingText',
                                               3: 'headingDescription',
                                               4: 'headingID',
                                               5: "REGULATION",
                                               6: 'PART',
                                               7: 'DIVISION',
                                               8: 'SUBDIVISION',
                                               9: 'SUBDIVISION CONTEXT',
                                               10: 'SECTION CONTEXT',
                                               11: 'SECTION',
                                               12: 'SUBSECTION CONTEXT',
                                               13: 'SUBSECTION',
                                               14: 'PARAGRAPH',
                                               15: 'SUBPARAGRAPH',
                                               16: 'CLAUSE'})


# print(pageData)
# C:\Users\alton\Documents\webPageData.csv
# C:\Users\Dragonfly\Documents\webPageData.csv
# sfcr.tsv
# fdr.tsv
pageData.to_csv(r'C:\Users\Dragonfly\Documents\fdr.tsv',
                index=False,
                sep='\t',
                quotechar='"',
                header=True,
                quoting=1)

definitions.to_csv(r'C:\Users\Dragonfly\Documents\fdr_definitions.csv',
                   index=False,
                   sep='\t',
                   quotechar='"',
                   header=True,
                   quoting=1)