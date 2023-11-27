import argparse
import logging
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """Function to parse command line arguments."""
    parser = argparse.ArgumentParser(description='A script to combine labels.')
    parser.add_argument('-f', '--file',
                        default='force-app/main/default/labels/CustomLabels.labels-meta.xml')
    parser.add_argument('-d', '--directory', default='force-app/main/default/labels')
    args = parser.parse_args()
    return args


def read_individual_xmls(label_directory):
    """Read each XML file."""
    individual_xmls = []
    for filename in os.listdir(label_directory):
        if filename.endswith('.xml') and not filename.endswith('.labels-meta.xml'):
            tree = ET.parse(os.path.join(label_directory, filename))
            root = tree.getroot()
            individual_xmls.append(root)

    return individual_xmls


def merge_xml_content(individual_roots):
    """Merge XMLs for all objects."""
    combined_root = ET.Element('CustomLabels', xmlns="http://soap.sforce.com/2006/04/metadata")

    for root in individual_roots:
        child_element = ET.Element(root.tag)
        combined_root.append(child_element)
        child_element.extend(root)

    return combined_root


def format_and_write_xml(combined_root, label_file):
    """Create the final XML."""
    xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str = ET.tostring(combined_root, encoding='utf-8').decode('utf-8')
    formatted_xml = minidom.parseString(xml_str).toprettyxml(indent="    ")

    # Remove extra new lines
    formatted_xml = '\n'.join(line for line in formatted_xml.split('\n') if line.strip())

    # Remove existing XML declaration
    formatted_xml = '\n'.join(line for line in formatted_xml.split('\n') if not line.strip().startswith('<?xml'))

    with open(label_file, 'wb') as file:
        file.write(xml_header.encode('utf-8'))
        file.write(formatted_xml.encode('utf-8'))


def combine_labels(label_directory, label_file):
    """Combine the labels for deployments."""
    individual_roots = read_individual_xmls(label_directory)
    combined_root = merge_xml_content(individual_roots)
    format_and_write_xml(combined_root, label_file)

    logging.info('The custom labels have been compiled for deployments.')


def main(directory, label_file):
    """Main function."""
    combine_labels(directory, label_file)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.directory, inputs.file)
