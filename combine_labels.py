import argparse
import logging
import os
import xml.etree.ElementTree as ET


logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """ Function to parse command line arguments."""
    parser = argparse.ArgumentParser(description='A script to create the deploy label file.')
    parser.add_argument('-f', '--file',
                        default='force-app/main/default/labels/CustomLabels.labels-meta.xml')
    parser.add_argument('-d', '--directory', default='force-app/main/default/labels')
    args = parser.parse_args()
    return args


def create_combined_label_file(output_dir, combined_file):
    """Create the combined label file for deployments."""
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
    with open(combined_file, 'wb') as xml_file:
        # Include encoding information in the XML header
        xml_file.write(xml_header.encode('utf-8'))
        for labels_string in labels_strings:
            # Remove existing XML declaration
            formatted_labels_string = '\n    '.join(line for line in labels_string.split('\n') if not line.strip().startswith('<?xml'))
            formatted_labels_string = formatted_labels_string.replace('<labels>', '        <labels>')
            xml_file.write(formatted_labels_string.encode('utf-8'))
            xml_file.write('\n'.encode('utf-8'))  # Add a newline between <labels> blocks
        xml_file.write(xml_footer.encode('utf-8'))

    logging.info('The custom labels have been compiled for deployments.')


def main(output_directory, output_file):
    """ Main function."""
    create_combined_label_file(output_directory, output_file)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.directory, inputs.file)
