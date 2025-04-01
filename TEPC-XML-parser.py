import xml.etree.ElementTree as ET
import pandas as pd
from dateutil import parser
from datetime import datetime
from dateutil.parser import ParserError

import os

#set the names for the output
column_names = [
    "Person_Observation_ID",
    "Source",
    "Document date",
    "Person Name",
    "Standardized Name",
    "Role",
    "Patronym",
    "Is this person unnamed?",
    "Enslaved By",
]


def main():
    source_folder = "source"  # Directory containing XML files

    # List all XML files in the 'source' folder
    xml_files = [f for f in os.listdir(source_folder) if f.endswith(".xml")]

    # Initialize a list to store all rows for the final DataFrame
    all_rows = []

    # Iterate over each XML file in the 'source' folder
    for xml_file in xml_files:
        xml_path = os.path.join(source_folder, xml_file)

        with open(xml_path, "rb") as file:
            # Parse the XML file
            tree = ET.parse(file)
            root = tree.getroot()

        docs = find_documents(root)
        keys = docs.keys()

        clean_docs = []

        for key in keys:
            doc = docs[key]
            clean_docs.append(
                cleanDoc(key, parse_doc_date(doc), parse_doc_people(doc, key))
            )

        # Append data from the cleaned documents to the all_rows list
        for d in clean_docs:
            if d.date:
                date = d.date.date()
            else:
                date = ""
            for p in d.people:
                all_rows.append(
                    [
                        p.uri,
                        d.ref,
                        date,
                        p.name,
                        p.reg_name,
                        p.role,
                        p.patronym,
                        check_appellation(p.reg_name),
                        enslavers_cell_value(p.enslavers),
                    ]
                )

    # Create a DataFrame from all collected rows
    df = pd.DataFrame(all_rows, columns=column_names)

    # Save the DataFrame to a CSV file
    df.to_csv("output.csv", index=False, encoding="utf-8")

#define a class to save person information in
class Person:
    _uri_counter = 1  # Class variable to track unique IDs

    def __init__(self, name, reg_name, role, patronym="", enslavers=[]):
        self.uri = Person._uri_counter  # Assign unique ID
        Person._uri_counter += 1  # Increment for the next object

        self.name = name
        self.reg_name = reg_name
        self.role = role
        self.patronym = patronym
        self.enslavers = enslavers

    def __str__(self):
        return f"ID: {self.uri} - name: {self.name} - reg_name: {self.reg_name} - role {self.role}"


#define a class to save the document information in, which covers multiple people
class cleanDoc:
    def __init__(self, ref, date: datetime, people: list[Person]):
        if not isinstance(date, datetime):
            #handle invalid dates found in the material
            if date == "YYYY" or date == None:
                date = None
            else:
                print(date)
                raise TypeError("date must be a datetime object")
        if not all(isinstance(person, Person) for person in people):
            raise TypeError("people must be a list of Person objects")

        self.ref = ref
        self.date = date
        self.people = people

#outputs a cleaned name, or no name if there is none.
def clean_name(name):
    if type(name) == type(None):
        return ""

    else:
        name = "".join(name.splitlines())
        name = " ".join(name.split())
        return name


def parse_doc_people(document, ref):

    output = []

    head = document.find("head")

    people = [node for node in head.findall(".//name") if node.get("type") == "person"]

    #check to make sure there are never more than two people tagged in the head-section of the inventory
    if len(people) > 2:
        print("found more than two people in the head")

    if len(people) < 1:
        print(f"found no people in the head of {ref}")

    count = 1
    for name in people:
        reg = name.get("reg")
        if count == 1:
            role = "deceased"
        if count == 2:
            role = "undefined partner of deceased"

        name = clean_name(name.text)

        output.append(Person(name, reg, role))
        count += 1

    # create list of enslavers
    enslavers = []
    for p in output:
        enslavers.append(p.uri)

    # add enslaved people
    enslaved_rows = [
        node for node in document.findall(".//row") if node.get("role") == "slave"
    ]
    enslaved_names = [
        n
        for row in document.findall('.//row[@role="slave"]')
        for n in row.findall(".//name")
        if n.get("type") == "person"
    ]

    for x in enslaved_names:
        reg = x.get("reg")
        role = "enslaved"
        name = clean_name(x.text)
        patronym = patro_from_reg(reg)

        output.append(Person(name, reg, role, patronym, enslavers))
    return output

def parse_doc(document, ref):
    people = parse_doc_people(document, ref)
    date = parse_doc_date(document)

    return cleanDoc(ref, date, people)


def parse_doc_date(document):
    # parses document and returns a datetime object

    head = document.find("head")
    date = head.find("./date")

    datestring = date.get("value")

    try:
        yourdate = parser.parse(datestring)
        return yourdate

    except ParserError:
        return None

def find_documents(root):
    div_dict = {}  # Dictionary to store div elements by 'n' attribute
    for node in root.findall(".//div"):
        n_value = node.get("n")
        if n_value:  # Ensure the 'n' attribute exists
            div_dict[n_value] = node  # Store node in dictionary
    return div_dict


def patro_from_reg(reg):
    if type(reg) != type(None):
        if "," in reg and "van" in reg:
            patroniem = reg.split(",")[0]

            return patroniem

        else:
            return ""

    else:
        return ""

def check_appellation(reg):
    if type(reg) == type(None):
        return True

    no_name_indicators = ["no name", "unnamed"]

    for i in no_name_indicators:
        if i in reg:
            return True

    return False


def enslavers_cell_value(enslavers):
    cell_value = ""
    for e in enslavers:
        cell_value = cell_value + str(e) + ";"

    cell_value = cell_value.rstrip(";")

    return cell_value

if __name__ == "__main__":
    main()
