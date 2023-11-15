import argparse
import logging
import xml.etree.ElementTree as ET
import os

ns = {'sforce': 'http://soap.sforce.com/2006/04/metadata'}
logging.basicConfig(format='%(message)s', level=logging.DEBUG)
XML_TAGS = ['alerts', 'fieldUpdates', 'flowActions', 'fullName', 'knowledgePublishes', 'outboundMessages', 'rules', 'tasks']


def parse_args():
    """
        Function to parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='A script to create workflows.')
    parser.add_argument('-o', '--output', default='force-app/main/default/workflows')
    args = parser.parse_args()
    return args


def extract_full_name(element, namespace):
    """Extract the full name from a given XML element."""
    full_name_element = element.find('sforce:fullName', namespace)
    return full_name_element.text if full_name_element is not None else None


def create_xml_file(label, workflow_directory, parent_workflow_name, tag, full_name):
    """Create a new XML file for a given element."""
    output_filename = f'{workflow_directory}/{parent_workflow_name}.{tag}_{full_name}.xml'

    # Remove the namespace prefix from the element tags
    for element in label.iter():
        if '}' in element.tag:
            element.tag = element.tag.split('}')[1]

    # Create a new XML ElementTree with the label as the root
    element_tree = ET.ElementTree(label)

    # Create a new XML file for each element
    with open(output_filename, 'wb') as file:
        # Add the XML header to the file
        file.write(b'<?xml version="1.0" encoding="UTF-8"?>\n    ')
        element_tree.write(file, encoding='utf-8')

    logging.info(f"Saved {tag} element content to {output_filename}")


def process_workflow_file(workflow_directory, filename):
    """Process a single workflow file and extract elements."""
    # Extract the parent workflow name from the XML file name
    parent_workflow_name = filename.split('.')[0]
    workflow_file_path = os.path.join(workflow_directory, filename)

    tree = ET.parse(workflow_file_path)
    root = tree.getroot()

    # Iterate through the specified XML tags
    for tag in XML_TAGS:
        for _, label in enumerate(root.findall(f'sforce:{tag}', ns)):
            full_name = extract_full_name(label, ns)

            if full_name:
                create_xml_file(label, workflow_directory, parent_workflow_name, tag, full_name)
            else:
                logging.info(f"Skipping {tag} element without fullName")


def separate_workflows(workflow_directory):
    """Separate workflows into individual XML files."""
    # Iterate through the directory to process files
    for filename in os.listdir(workflow_directory):
        if filename.endswith(".workflow-meta.xml"):
            process_workflow_file(workflow_directory, filename)


def main(output_directory):
    """
    Main function
    """
    separate_workflows(output_directory)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.output)
