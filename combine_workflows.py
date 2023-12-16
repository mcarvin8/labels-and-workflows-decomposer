import argparse
import logging
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """Function to parse command line arguments."""
    parser = argparse.ArgumentParser(description='A script to create workflows.')
    parser.add_argument('-d', '--directory', default='force-app/main/default/workflows')
    args = parser.parse_args()
    return args


def read_individual_xmls(workflow_directory):
    """Read each XML file."""
    individual_xmls = {}
    for filename in os.listdir(workflow_directory):
        if filename.endswith('.xml') and not filename.endswith('.workflow-meta.xml'):
            parent_workflow_name = filename.split('.')[0]
            individual_xmls.setdefault(parent_workflow_name, [])

            tree = ET.parse(os.path.join(workflow_directory, filename))
            root = tree.getroot()
            individual_xmls[parent_workflow_name].append(root)

    # Sort by workflow type and then alphabetically
    sorted_individual_xmls = {k: sorted(v, key=lambda x: x.tag) for k, v in sorted(individual_xmls.items())}

    return sorted_individual_xmls


def merge_xml_content(individual_xmls):
    """Merge XMLs for each object."""
    merged_xmls = {}
    for parent_workflow_name, individual_roots in individual_xmls.items():
        parent_workflow_root = ET.Element('Workflow', xmlns="http://soap.sforce.com/2006/04/metadata")

        # Sort individual_roots by tag to match Salesforce CLI output
        individual_roots.sort(key=lambda x: x.tag)

        for root in individual_roots:
            child_element = ET.Element(root.tag)
            parent_workflow_root.append(child_element)
            child_element.extend(root)

        merged_xmls[parent_workflow_name] = parent_workflow_root

    return merged_xmls


def format_and_write_xmls(merged_xmls, workflow_directory):
    """Create the final XMLs."""
    xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    for parent_workflow_name, parent_workflow_root in merged_xmls.items():
        parent_xml_str = ET.tostring(parent_workflow_root, encoding='utf-8').decode('utf-8')
        formatted_xml = minidom.parseString(parent_xml_str).toprettyxml(indent="    ")

        # Remove extra new lines
        formatted_xml = '\n'.join(line for line in formatted_xml.split('\n') if line.strip())

        # Remove existing XML declaration
        formatted_xml = '\n'.join(line for line in formatted_xml.split('\n') if not line.strip().startswith('<?xml'))

        parent_workflow_filename = os.path.join(workflow_directory, f'{parent_workflow_name}.workflow-meta.xml')
        with open(parent_workflow_filename, 'wb') as file:
            file.write(xml_header.encode('utf-8'))
            file.write(formatted_xml.encode('utf-8'))


def combine_workflows(workflow_directory):
    """Combine the workflows for deployments."""
    individual_xmls = read_individual_xmls(workflow_directory)
    merged_xmls = merge_xml_content(individual_xmls)
    format_and_write_xmls(merged_xmls, workflow_directory)

    logging.info('The workflows have been compiled for deployments.')


def main(directory):
    """Main function."""
    combine_workflows(directory)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.directory)
