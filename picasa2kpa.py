from __future__ import print_function

__author__ = 'dinel'

import codecs
from lxml import etree
import os
import pyexiv2
import re
import sys

import utils


def check_keywords(doc):
    """

    :param doc:
    :return: None
    """
    keywords = utils.get_list_keywords(doc)

    for (key, dummy) in keywords:
        if "external_info" == key: return

    # if I get here there is no keyword external_info, so create one
    dummy, kid = max(keywords, key=lambda x: int(x[1]))
    etree.SubElement(doc.xpath("//Categories/Category[@name='Keywords']")[0], "value",
                     value="external_info", id=str(int(kid) + 1))


def check_person(doc, name):
    """

    :param doc:
    :return: None
    """
    persons = utils.get_list_persons(doc)

    for (key, dummy) in persons:
        if name == key: return

    # if I get here there is no person with the given name, so create one
    dummy, pid = max(persons, key=lambda x: int(x[1]))
    etree.SubElement(doc.xpath("//Categories/Category[@name='Persons']")[0], "value",
                     value=name, id=str(int(pid) + 1))

def insert_person(doc, node, person):
    # check whether the person exists in the list of persons
    """

    :param doc:
    :param node:
    :param person:
    """
    check_person(doc, person)
    if doc.xpath("//image[@md5sum='%s']/options/option[@name='Persons']/value[@value='%s']" % (node.get("md5sum"), person)):
        pass
    else:
        if not doc.xpath("//image[@md5sum='%s']/options" % node.get("md5sum")):
            etree.SubElement(doc.xpath("//image[@md5sum='%s']" % node.get("md5sum"))[0], "options")

        if not doc.xpath("//image[@md5sum='%s']/options/option[@name='Persons']" % node.get("md5sum")):
            etree.SubElement(doc.xpath("//image[@md5sum='%s']/options" % node.get("md5sum"))[0], "option", name="Persons")

        if not doc.xpath("//image[@md5sum='%s']/options/option[@name='Keywords']" % node.get("md5sum")):
            etree.SubElement(doc.xpath("//image[@md5sum='%s']/options" % node.get("md5sum"))[0], "option", name="Keywords")

        etree.SubElement(doc.xpath("//image[@md5sum='%s']/options/option[@name='Persons']" % node.get("md5sum"))[0],
                         "value", value=person)
        etree.SubElement(doc.xpath("//image[@md5sum='%s']/options/option[@name='Keywords']" % node.get("md5sum"))[0],
                         "value", value="external_info")


def process_images(path2index, doc, mappings):
    """

    :param doc:
    :param mappings:
    """
    no_images = len(doc.xpath("//images/image"))
    for count, image in enumerate(doc.xpath("//images/image")):
        print("\rProcessing %5d of %d (%3d%%)" % ((count + 1), no_images, (100 * count / no_images)), end="")
        path2file = image.get("file")
        if path2file and os.path.isfile(path2index + path2file):
            try:
                img = pyexiv2.metadata.ImageMetadata(path2index + path2file)
                img.read()
            except IOError:
                # the file cannot be read or more likely it is not an image
                # TODO: have proper testing if it is an image
                continue

            for key in img.xmp_keys:
                if re.search(":Name$", key):
                    tag = img.__getitem__(key)
                    if tag.value in mappings: insert_person(doc, image, mappings[tag.value])

def read_mappings(mapping_file):
    """

    :rtype : dict
    :return:
    """
    mappings = {}

    try:
        for line in codecs.open(mapping_file, "r", encoding="utf8"):
            match = re.search(r"^([^:]+):(.+)$", line.strip())
            if match:
                mappings[match.group(1)] = match.group(2)
            else:
                print("Skipping mapping: " + line)
    except IOError as e:
        print("The mappings could not be read ({0}): {1}".format(e.errno, e.strerror))
        sys.exit(-1)

    return mappings


if __name__ == "__main__":

    args = utils.create_arguments_parser()
    print(args)

    path2index = args.directory

    doc = utils.read_document(path2index)
    if not args.no_checking:
        if not utils.verify_version(doc):
            print("Incorrect version used")
            sys.exit(-2)
        else:
            print("Correct version found")

    # read the mappings
    mappings = read_mappings(args.mapping)

    # check the keywords and update them if necessary
    check_keywords(doc)

    # process images
    process_images(path2index, doc, mappings)
    doc.write("output.xml")