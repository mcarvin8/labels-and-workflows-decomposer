"""
    Build invidual label files from the retrieval file for version control.
"""
import argparse
import logging
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
    parser.add_argument('-o', '--output', default='force-app/main/default/labels')
    args = parser.parse_args()
    return args


def create_individual_label_files(xml_file_path, output_directory):
    """
    Create individual label dictionaries from an XML file.
    """
    xml_tags = ['fullName', 'categories', 'language', 'protected', 'shortDescription', 'value']
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # Iterate through the 'labels' elements and create dictionaries
        for label in root.findall('sforce:labels', ns):
            label_dict = {}
            for tag in xml_tags:
                tag_object = label.find(f'sforce:{tag}', ns)
                if tag_object is not None:
                    label_dict[tag] = tag_object.text

            formatted_xml = ET.Element('labels')
            for key, value in label_dict.items():
                ET.SubElement(formatted_xml, key).text = value

            xml_string = minidom.parseString(ET.tostring(formatted_xml)).toprettyxml(indent="    ")
            label_name = label_dict['fullName']
            label_file_path = f'{output_directory}/{label_name}.xml'

            with open(label_file_path, 'w', encoding='utf-8') as xml_file:
                xml_file.write(xml_string)

    except FileNotFoundError:
        logging.info("Error: XML file '%s' not found.", xml_file_path)
    except ET.ParseError:
        logging.info("Error: Unable to parse the XML file.")


def main(combined_file, output_directory):
    """
    Main function to run the script.
    """
    create_individual_label_files(combined_file, output_directory)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.xmls, inputs.output)
