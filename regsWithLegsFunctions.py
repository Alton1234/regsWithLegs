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

def proc_marginalnote(tag):
    """Processes headings and returns an array that contains
        the heading level, heading type, heading name, heading text"""