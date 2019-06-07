import pandas as pd


def clean_text(rawtext):
    text = (rawtext.
            replace('\xa0', '').
            replace('\xe2\x80\x9c', '“').
            replace('\xe2\x80\x9d', '”').
            replace('\xe2\x80\x94', '-'))
    return text


# Processes received lists into a cleaned format for the data table
def clean_data(dirtyList):
    # Variable assignment for cleaning
    headingLevel = dirtyList[0]
    headingType = dirtyList[1]
    headingText = str(dirtyList[2])
    headingDescription = clean_text(dirtyList[3])
    headingID = dirtyList[4]

    # **** Variable cleaning ****

    # list heading types and what to parse out
    replaceString = {
        "PART ": "",
        "SECTION ": "",
        "SUBSECTION ": "",
        "PARAGRAPH ": "",
        "SUBPARAGRAPH ": "",
        "CLAUSE ": "",
        "DIVISION ": "",
        "SUBDIVISION ": ""
    }

    fullTextRemove = ["PART", "SECTION", "DIVISION", "SUBDIVISION"]  # All of the listed text will be removed
    partialTextRemove = ["SUBSECTION", "PARAGRAPH", "SUBPARAGRAPH", "CLAUSE"]  # Only "(" and ")" will be removed

    headingType = headingType.upper()  # Capitalizes all characters

    # cleans text to leave only code values, in some cases there are no codes and full text will remain
    if headingType in fullTextRemove:
        headingText = headingText.replace(headingType, "")
    elif headingType in partialTextRemove:
        headingText = headingText.replace("(", "")
        headingText = headingText.replace(")", "")

    headingText = headingText.strip()  # Remove any leading and trailing whitespace from code values

    # Returns list of cleaned values
    return [headingLevel,
            headingType,
            headingText,
            headingDescription,
            headingID]


def create_dataframe(inputList):
    """ Creates a panadas dataframe to append to the master dataset"""
    return pd.DataFrame([[
        inputList[0],
        inputList[1],
        inputList[2],
        inputList[3],
        inputList[4],
        inputList[5],
        inputList[6],
        inputList[7],
        inputList[8],
        inputList[9],
        inputList[10],
        inputList[11],
        inputList[12],
        inputList[13],
    ]])


def proc_heading(tag, level, counter):
    """Processes headings and returns an array that contains
    the heading level, heading type, heading name, heading text"""

    headingtype = {
        "h2": "Part",
        "h3": "Division",
        "h4": "Subdivision",
        "h5": "Subdivision Context"}


    headinglevel = level # Retrieves heading level IE: 1 = part
    headingtype = headingtype[tag.name]  # Defines the type of variable by the HTML class

    if headingtype == "Subdivision Context":
        headingtext = str(counter)
    else:
        headingtext = list(tag)[0].get_text()  # Contains the part number etc

    if len(list(tag)) > 1:
        headingdescription = list(tag)[1].get_text()  # Contains the description, if any
    else:
        headingdescription = ''

    headingid = tag.get('id')

    cleanList = clean_data([headinglevel, headingtype, headingtext, headingdescription, headingid])
    return cleanList


def proc_marginalnote(tag, level, notetype, counter):
    """Processes marginal notes and returns an array that contains
        the heading level, heading type, heading name, heading text"""

    headinglevel = level  # Retrieves heading level IE: 1 = part
    headingtype = notetype
    headingtext = str(counter)  # Contains the part number etc
    headingdescription = tag.find(text=True, recursive=False)  # Marginal notes do not have associated descriptions
    headingid = tag.get('id')

    cleanList = clean_data([headinglevel, headingtype, headingtext, headingdescription, headingid])
    return cleanList


def proc_section(tag, level):
    """Processes section and returns an array that contains
    the heading level, heading type, heading name, heading text"""
    subcode = tag.find(class_="sectionLabel")
    tempitem = tag
    tempitem.strong.extract()

    headinglevel = level  # Retrieves heading level IE: 1 = part
    headingtype = tag.get('class')[0]
    headingtext = subcode.get_text() # Contains the part number etc
    headingdescription = tempitem.get_text()  # Marginal notes do not have associated descriptions
    headingid = subcode.get('id')

    cleanList = clean_data([headinglevel, headingtype, headingtext, headingdescription, headingid])
    return cleanList


def proc_subsection(tag):
    """<p class='subSection'> have one of the following structures:
    1. SECTION(SUB SECTION) or
    2. (SUB SECTION)
    The differentiation is important as type 1 needs to have the section split out of it in
    the case of a section, the class type will be sectionLabel, subsections will have class lawlabel"""
    outputlist = ['start of list']
    # Check for presence of section label, which is always wrapped in <strong>
    # The definition itself will be tied to the subsection, not the section in this case
    if len(tag.find_all('strong')) == 1:
        sectiontag = tag.find(class_='sectionLabel')

        headinglevel = 6 # Section
        headingtype = 'section'
        headingtext = sectiontag.get_text()
        headingdescription = ""
        headingid = sectiontag.get('id')

        cleanList = clean_data([headinglevel, headingtype, headingtext, headingdescription, headingid])
        # Generates entry to add too list
        outputlist.append(cleanList)

    if len(tag.find_all(class_='lawLabel')) > 0:
        subTag = tag.find(class_="lawLabel")
        headinglevel = 8  # Subsection, this may need to change
        headingtype = 'Subsection'
        headingtext = subTag.get_text()
        headingid = subTag.get('id')
        subTag = subTag.parent  # Step up to parent
        headingdescription = subTag.find_all(text=True, recursive=False)
        if len(headingdescription) > 1:
            headingdescription = headingdescription[1]
        else:
            headingdescription = headingdescription[0]

        # Generates entry to add too list
        cleanList = clean_data([headinglevel, headingtype, headingtext, headingdescription, headingid])
        outputlist.append(cleanList)

    del outputlist[0]  # Removes first faux entry
    return outputlist


def proc_paragraph(tag):
    """Processes tags with class paragraph, sub paragraphs, and Clauses"""

    #Assigns level based on class
    classlevel = {
        'Paragraph': 9,
        'Subparagraph': 10,
        'Clause': 11
    }
    sublevel = classlevel[tag.get('class')[0]]
    subClass = tag.get('class')[0]

    # S1: retrieve lawLable object
    subTag = tag.find(class_="lawLabel")

    headinglevel = sublevel
    headingtype = subClass
    headingtext = subTag.get_text()  # Contains the part number etc
    headingid = subTag.get('id')

    subTag = subTag.parent
    headingdescription = subTag.find_all(text=True, recursive=False)
    if len(headingdescription) > 1:
        headingdescription = headingdescription[1]
    else:
        headingdescription = headingdescription[0]

    cleanList = clean_data([headinglevel, headingtype, headingtext, headingdescription, headingid])
    return cleanList


def proc_provisions(tag, counter, blocklevel):
    """Processes provisions, this is a recursive function as the depth of these
    lists are otherwise unknown"""

    outputlist = ['start of list']  # Initiate list
    for lists in tag.find_all(recursive=False):
        for items in lists.find_all(recursive=False):
            # S2: There should only be <p> and <ul> at this point, in the case of <p> scrape contents
            if items.name == 'p':
                if items.get('class')[0] == 'Subsection':
                    outputlist.extend(proc_subsection(items))
                elif items.get('class')[0] == 'MarginalNote':
                    counter += 1
                    outputlist.append(proc_marginalnote(items,
                                                        blocklevel['SUBSECTION CONTEXT'],
                                                        'SUBSECTION CONTEXT',
                                                        counter))
                elif items.get('class')[0] == 'Paragraph':
                    outputlist.append(proc_paragraph(items))
                elif items.get('class')[0] == 'Subparagraph':
                    outputlist.append(proc_paragraph(items))
                elif items.get('class')[0] == 'Clause':
                    outputlist.append(proc_paragraph(items))

            if items.name == 'ul':
                outputlist.extend(proc_provisions(items, counter))

    del outputlist[0]  # Removes first faux entry
    return outputlist
