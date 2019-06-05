def clean_text(rawtext):
    text = (rawtext.
            replace('\xa0', ' ').
            replace('\xe2\x80\x9c', ' ').
            replace('\xe2\x80\x9d', '“').
            replace('\xe2\x80\x94', '”'))
    return text

def proc_heading(tag, level):
    """Processes headings and returns an array that contains
    the heading level, heading type, heading name, heading text"""

    headinglevel = level # Retrieves heading level IE: 1 = part
    headingtype = list(tag.get('class'))[0]  # Defines the type of variable by the HTML class
    headingtext = list(tag)[0].get_text()  # Contains the part number etc

    if len(list(tag)) > 1:
        headingdescription = list(tag)[1].get_text()  # Contains the description, if any
    else:
        headingdescription = ''

    headingid = tag.get('id')

    return [headinglevel, headingtype, headingtext, headingdescription, headingid]


def proc_marginalnote(tag, level):
    """Processes marginal notes and returns an array that contains
        the heading level, heading type, heading name, heading text"""

    headinglevel = level  # Retrieves heading level IE: 1 = part
    headingtype = tag.get('class')[0]
    headingtext = tag.find(text=True, recursive=False)  # Contains the part number etc
    headingdescription = ''  # Marginal notes do not have associated descriptions
    headingid = tag.get('id')

    return [headinglevel, headingtype, headingtext, headingdescription, headingid]

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

    return [headinglevel, headingtype, headingtext, headingdescription, headingid]

def proc_subsection(tag, subLevel):
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

        headinglevel = 6 # subSection
        headingtype = 'sectionLabel'
        headingtext = sectiontag.get_text()
        headingdescription = ""
        headingid = sectiontag.get('id')

        # Generates entry to add too list
        outputlist.append([headinglevel, headingtype, headingtext, headingdescription, headingid])

    if len(tag.find_all(class_='lawLabel')) > 0:
        subTag = tag.find(class_="lawLabel")
        headinglevel = subLevel  # Subsection, this may need to change
        headingtype = 'lawLabel'
        headingtext = subTag.get_text()
        headingid = subTag.get('id')
        subTag = subTag.parent  # Step up to parent
        headingdescription = subTag.find_all(text=True, recursive=False)
        if len(headingdescription) > 1:
            headingdescription = headingdescription[1]
        else:
            headingdescription = headingdescription[0]

        # Generates entry to add too list
        outputlist.append([headinglevel, headingtype, headingtext, headingdescription, headingid])

    del outputlist[0]  # Removes first faux entry

    return outputlist

def proc_paragraph(tag):
    """Processes tags with class paragraph, sub paragraphs, and Clauses"""

    #Assigns level based on class
    classlevel = {
        'Paragraph': 7,
        'Subparagraph': 8,
        'Clause': 9
    }
    sublevel = classlevel[tag.get('class')[0]]

    #S1: retrieve lawLable object
    subTag = tag.find(class_="lawLabel")

    headinglevel = sublevel
    headingtype = 'lawLabel'
    headingtext = subTag.get_text()  # Contains the part number etc
    headingid = subTag.get('id')

    subTag = subTag.parent

    headingdescription = subTag.find_all(text=True, recursive=False)
    if len(headingdescription) > 1:
        headingdescription = headingdescription[1]
    else:
        headingdescription = headingdescription[0]

    return [headinglevel, headingtype, headingtext, headingdescription, headingid]

def proc_provisions(tag):
    """Processes provisions, this is a recursive function as the depth of these
    lists are otherwise unknown"""

    outputlist = ['start of list']  # Initiate list
    for lists in tag.find_all(recursive=False):
        for items in lists.find_all(recursive=False):
            # S2: There should only be <p> and <ul> at this point, in the case of <p> scrape contents
            if items.name == 'p':
                # Subsection processing
                if items.get('class')[0] == 'Subsection':
                    outputlist.extend(proc_subsection(items, 7))
                elif items.get('class')[0] == 'MarginalNote':
                    outputlist.append(proc_marginalnote(items, 5))
                elif items.get('class')[0] == 'Paragraph':
                    outputlist.append(proc_paragraph(items))
                elif items.get('class')[0] == 'Subparagraph':
                    outputlist.append(proc_paragraph(items))
                elif items.get('class')[0] == 'Clause':
                    outputlist.append(proc_paragraph(items))

            if items.name == 'ul':
                #outputlist.append("recursive")
                outputlist.extend(proc_provisions(items))

    del outputlist[0]  # Removes first faux entry
    return outputlist
