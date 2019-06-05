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

    return [[headinglevel, headingtype, headingtext, headingdescription, headingid]]


def proc_marginalnote(tag, level):
    """Processes marginal notes and returns an array that contains
        the heading level, heading type, heading name, heading text"""

    headinglevel = level  # Retrieves heading level IE: 1 = part
    headingtype = tag.get('class')[0]
    headingtext = tag.find(text=True, recursive=False)  # Contains the part number etc
    headingdescription = ''  # Marginal notes do not have associated descriptions
    headingid = tag.get('id')

    return [[headinglevel, headingtype, headingtext, headingdescription, headingid]]

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

    return [[headinglevel, headingtype, headingtext, headingdescription, headingid]]


