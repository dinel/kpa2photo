from __future__ import print_function

'''
  picasa2kpa: program which transfer information about people embedded by programs such as Picasa in the KPhotoAlbum
  database

  This program is available under the GNU GPL v3.0 license
  Please ensure you make a backup of your data before you attempt using it
'''

__author__ = 'dinel'

import argparse
import codecs
from lxml import etree
import os
import pyexiv2
import re
import utils


def create_arguments_parser():
    parser = argparse.ArgumentParser(description=
                                     '''
                                     Utility script used to produce a skeleton of the mapping file.
                                     ''',
                                     epilog=
                                     '''More information can be found at https://github.com/dinel/kpa2photo''')
    parser.add_argument('-s', '--separator', default=':', help='The separator for the mapping')
    parser.add_argument('-m', '--mapping', default='person.map',
                        help='The file in which the mappings are written')
    parser.add_argument('directory', help='The directory that contains the index.xml file')

    return parser.parse_args()

def read_names_xml(doc):
    """

    :param doc:
    :return:
    """
    return [name.get("value") for name in doc.xpath("//Category[@name='Persons']/value")]


def read_names_imgs(doc, path):
    """

    TODO: check this code because most of it is duplicate of function process_image

    :param doc:
    :param path:
    :return:
    """
    imgs_names = []
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
                    imgs_names.append(tag.value)

    return sorted(set(imgs_names))


def find_similar(name, list_names):
    s_2 = set(name.split(" "))
    return [n for n in list_names if s_2 <= set(n.split(" ") or s_2 >= set(n.split(" ")))]


if __name__ == "__main__":

    args = utils.create_arguments_parser()
    print(args)

    path2index = args.directory
    doc = utils.read_document(path2index)
    xml_names = read_names_xml(doc)
    imgs_names = read_names_imgs(doc, path2index)

    output = codecs.open(args.mapping, mode="w", encoding="utf8")

    for name in imgs_names:
        output.write(name + args.separator + ",".join(find_similar(name, xml_names)) + "\n")

    output.close()