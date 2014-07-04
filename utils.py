from __future__ import print_function

import sys
from lxml import etree

def get_list_elements(doc, tag_name):
    """
    Returns a list of pairs (string, id). The actual string depends on the tag_name provided

    :param doc: the root document
    :param tag_name: the tag name to be estracted
    :rtype : list
    :return a list of paris
    """
    return [(val.get("value"), val.get("id"))
            for val in doc.xpath("//Categories/Category[@name='" + tag_name + "']/value")]


def get_list_keywords(doc):
    """
    Returns the list of pairs (keyword, id) as defined in the index.xml file
    :param doc: the root of the index.xml file
    :rtype: list
    :return: a list which contains all the keywords as defined in the index.xml file
    """
    return get_list_elements(doc, "Keywords")


def get_list_persons(doc):
    """
    Returns the list of pairs (person name, id) as defined in the index.xml file
    :param doc: the root of the index.xml file
    :rtype: list
    :return: a list which contains all the names as defined in the index.xml file
    """
    return get_list_elements(doc, "Persons")


def match_names(xml_names, photos_names):
    """

    :param xml_names:
    :param photos_names:
    """
    pass


def read_document(path2file):
    """

    :param path2file:
    :return:
    """
    print("Reading the index file ..... ", end="")
    sys.stdout.flush()
    doc = etree.parse(path2file + "index.xml")
    print("done!")
    sys.stdout.flush()

    return doc


def verify_version(doc):
    """
    Verifies whether the correct version of the XML file is being used
    :param doc: the root document
    :return: True if the XML file is version 3 and uncompressed
    """
    # TODO: extend the code so it can handle other versions as well
    version = doc.iter('KPhotoAlbum').next()
    if "3" == version.get('version') and "0" == version.get('compressed'):
        return True
    else:
        return False
