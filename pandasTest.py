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
# Lists will never have a class and will always contain
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
page = requests.get("https://laws-lois.justice.gc.ca/eng/regulations/SOR-2018-108/FullText.html")

soup = BeautifulSoup(page.content, 'html.parser')
regContents = soup.find(id='docCont').find_all()  # returns all elements from the page


# Initializes a pandas data frame for heading data
titleOfAct = soup.find(class_="Title-of-Act").get_text()
subText = soup.find(class_='ChapterNumber').get_text()
tocFrame = pd.DataFrame([[0, "Title of Regulation", titleOfAct, subText, '']])  # Creates first entry

# Create a unique list of headings, this is what would be found in the table of contents in the sheet.
for item in regContents:
    # Part and schedule names, descriptions, and HTML ids
    if item.name == 'h2':
        # Variable assignment
        headingLevel = 1
        if list(item.get('class'))[0] == 'scheduleLabel':
            headingType = "Schedule"
        else:
            headingType = "Part"
        headingText = list(item)[0].get_text()  # Contains the part number etc
        headingDescription = list(item)[1].get_text()  # Contains the description, if any
        headingID = item.get('id')

        # Append data frame with new row
        tocFrame = tocFrame.append([[headingLevel,
                                     headingType,
                                     headingText,
                                     headingDescription,
                                     headingID]],
                                   ignore_index=True)

    # Division names, descriptions, and HTML ids
    elif item.name == 'h3':
        headingLevel = 2  # The hierarchical level of the heading
        headingType = "Division"  # The categorical type of the heading
        headingText = list(item)[0].get_text()  # Contains the part number etc
        if len(list(item)) > 1:
            headingDescription = list(item)[1].get_text()  # Contains the description, if any
        else:
            headingDescription = ''

        headingID = item.get('id')  # Html IDs for use in navigating to the entity on the web page

        # Append data frame with new row
        tocFrame = tocFrame.append([[headingLevel,
                                     headingType,
                                     headingText,
                                     headingDescription,
                                     headingID]],
                                   ignore_index=True)

    # Subdivision names, descriptions, and HTML ids
    elif item.name == 'h4':
        headingLevel = 3  # The hierarchical level of the heading
        headingType = "Subdivision"  # The categorical type of the heading
        headingText = list(item)[0].get_text()  # Contains the part number etc
        if len(list(item)) > 1:
            headingDescription = list(item)[1].get_text()  # Contains the description, if any
        else:
            headingDescription = ''

        headingID = item.get('id')  # Html IDs for use in navigating to the entity on the web page

        # Append data frame with new row
        tocFrame = tocFrame.append([[headingLevel,
                                     headingType,
                                     headingText,
                                     headingDescription,
                                     headingID]],
                                   ignore_index=True)

    # Subdivision names, descriptions, and HTML ids
    elif item.name == 'h5':
        headingLevel = 4  # The hierarchical level of the heading
        headingType = "Subdivision"  # The categorical type of the heading
        headingText = list(item)[0].get_text()  # Contains the part number etc
        if len(list(item)) > 1:
            headingDescription = list(item)[1].get_text()  # Contains the description, if any
        else:
            headingDescription = ''

        headingID = item.get('id')  # Html IDs for use in navigating to the entity on the web page

        # Append data frame with new row
        tocFrame = tocFrame.append([[headingLevel,
                                     headingType,
                                     headingText,
                                     headingDescription,
                                     headingID]],
                                   ignore_index=True)

# Marginal Notes names, descriptions
    elif 'class' in item.attrs:
        if len(item.get('class')) != 0:
            if item.get('class')[0] == 'MarginalNote':
                headingLevel = 5  # The hierarchical level of the heading
                headingType = "marginal Note"  # The categorical type of the heading
                headingText = list(item)[0].get_text()  # Contains the part number etc
                if len(list(item)) > 1:
                    headingDescription = list(item)[1].get_text()  # Contains the description, if any
                else:
                    headingDescription = ''

                headingID = item.get('id')  # Html IDs for use in navigating to the entity on the web page

                # Append data frame with new row
                tocFrame = tocFrame.append([[headingLevel,
                                             headingType,
                                             headingText,
                                             headingDescription,
                                             headingID]],
                                           ignore_index=True)



headingLevel = 4  # The hierarchical level of the heading

headingType = "Subdivision"  # The categorical type of the heading

headingText = list(item)[0].get_text()  # Contains the part number etc

if len(list(item)) > 1:

    headingDescription = list(item)[1].get_text()  # Contains the description, if any

else:

    headingDescription = ''

headingID = item.get('id')  # Html IDs for use in navigating to the entity on the web page

# Append data frame with new row

tocFrame = tocFrame.append([[headingLevel,

                             headingType,

                             headingText,

                             headingDescription,

                             headingID]],

                           ignore_index=True)
# Renames column names for readability
tocFrame = tocFrame.rename(index=str, columns={0: "headingLevel",
                                               1: "headingType",
                                               2: 'headingText',
                                               3: 'headingDescription',
                                               4: 'headingID'})
print(tocFrame)

export_csv = tocFrame.to_csv(r'C:\Users\alton\Documents\export_dataFrame.csv', index=None, header=True)
os.startfile('C:/Users/alton/Documents/export_dataFrame.csv')
# for item in definitions:
#     if isinstance(item.get('class'), (list,)):
#         if item.get('class')[0] == 'sectionLabel':
#             section = item.get_text()
#         elif item.get('class')[0] == 'lawLabel':
#             subSection = item.get_text()
#             print(section + " " + subSection)

# for item in definitions:
#     dfn = item.find(text=True, recursive=False) # First line of a definition
#     for subItem in item.find_all():
#         if subItem.name == 'dfn':
#             term = subItem.get_text() # The term that will be defined
#         if subItem.name ==
#             print(term + ": " + dfn)