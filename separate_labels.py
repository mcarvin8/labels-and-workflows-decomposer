"""
    Build invidual label files from the retrieval file for version control.
"""
import argparse
import logging
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom


ns = {'sforce': 'http://soap.sforce.com/2006/04/metadata'}
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
    Function to parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='A script to create custom labels files.')
    parser.add_argument('-x', '--xmls',
                        default='force-app/main/default/labels/CustomLabels.labels-meta.xml')
    args = parser.parse_args()
    return args


def separate_labels(xml_file_path):
    """
        Separate labels into their own files
    """
    parent_directory = os.path.dirname(xml_file_path)
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # Iterate through the 'labels' elements and create dictionaries
        for label in root.findall('sforce:labels', ns):
            label_dict = {}
            for tag_object in label.iter():
                if '}' in tag_object.tag:
                    tag = tag_object.tag.split('}')[-1]
                    label_dict[tag] = tag_object.text
                    logging.info(tag_object.text)

            formatted_xml = ET.Element('labels')
            for key, value in label_dict.items():
                if not value.isspace():
                    ET.SubElement(formatted_xml, key).text = value

            xml_string = minidom.parseString(ET.tostring(formatted_xml)).toprettyxml(indent="    ")
            label_name = label_dict.get('fullName', 'UnknownLabel')  # Default if 'fullName' is not present
            label_file_path = f'{parent_directory}/{label_name}.xml'

            with open(label_file_path, 'w', encoding='utf-8') as xml_file:
                xml_file.write(xml_string)

    except FileNotFoundError:
        logging.info("Error: XML file '%s' not found.", xml_file_path)
    except ET.ParseError:
        logging.info("Error: Unable to parse the XML file.")


def main(combined_file):
    """
        Main function.
    """
    separate_labels(combined_file)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.xmls)
