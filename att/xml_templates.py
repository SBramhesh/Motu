import os
from bs4 import BeautifulSoup
from os.path import exists


def return_dict():

    xml_files = []
    xml_dict = {}

    for x in os.listdir():
        if x.endswith(".xml"):
            xml_files.append(str(x)[:-4])

    for key in xml_files:
        if exists(f"{str(key)}.xml"):
            with open(f"{str(key)}.xml", "r", encoding='utf-8') as file:
                soup = BeautifulSoup(file, "xml")
                str(soup).replace('\n', '')
                xml_dict[key] = str(soup)
    return xml_dict
