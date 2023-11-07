"""
    Combine individual label files for deployments.
"""
import argparse
import logging
import os
import xml.etree.ElementTree as ET


ns = {'sforce': 'http://soap.sforce.com/2006/04/metadata'}
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
    Function to parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='A script to create the deploy label file.')
    parser.add_argument('-x', '--xmls',
                        default='force-app/main/default/labels/CustomLabels.labels-meta.xml')
    parser.add_argument('-o', '--output', default='force-app/main/default/labels')
    args = parser.parse_args()
    return args


def create_combined_label_file(output_dir, combined_file):
    """
    Create the combined label file for CI/CD use.
    """
    # Define the XML header and footer
    xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n<CustomLabels xmlns="http://soap.sforce.com/2006/04/metadata">\n'
    xml_footer = '</CustomLabels>\n'
    # Create a list to store the XML strings for each <labels> block
    labels_strings = []

    # Iterate through the individual XML files in the output directory
    for filename in os.listdir(output_dir):
        if filename == "CustomLabels.labels-meta.xml":
            continue  # Skip this file
        if filename.endswith(".xml"):
            file_path = os.path.join(output_dir, filename)
            tree = ET.parse(file_path)
            label_element = tree.getroot()
            labels_strings.append(ET.tostring(label_element, encoding='UTF-8').decode('utf-8'))

    # Save the combined XML to a file with proper formatting
    with open(combined_file, 'w', encoding='utf-8') as xml_file:
        xml_file.write(xml_header)
        for labels_string in labels_strings:
            xml_file.write(labels_string)
            xml_file.write('\n')  # Add a newline between <labels> blocks
        xml_file.write(xml_footer)

    logging.info("Combined XML file created with all labels using individual XML files in '%s'.",
                 combined_file)


def main(output_directory, output_file):
    """
    Main function to run the script.
    """
    create_combined_label_file(output_directory, output_file)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.output, inputs.xmls)
