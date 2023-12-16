import argparse
import logging
import sys
import xml.etree.ElementTree as ET

import combine_labels
import combine_workflows

LABEL_TYPE = ['CustomLabel']
INVALID_LABEL_TYPE = ['CustomLabels']
WORKFLOW_PARENT_TYPE = ['Workflow']
WORKFLOW_CHILD_TYPES = ['WorkflowAlert', 'WorkflowFieldUpdate', 'WorkflowFlowAction',
                  'WorkflowKnowledgePublish', 'WorkflowOutboundMessage', 'WorkflowRule',
                  'WorkflowTask']

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
ns = {'sforce': 'http://soap.sforce.com/2006/04/metadata'}


def parse_args():
    """Function to parse required arguments."""
    parser = argparse.ArgumentParser(description='A script to scan the package for labels and workflows.')
    parser.add_argument('-m', '--manifest', default='./manifest/package.xml')
    args = parser.parse_args()
    return args


def set_dictionary_members(package_members, package_dict):
    """Add metadata members in package to a dictionary."""
    for member in package_members:
        package_dict[member] = True
    return package_dict


def parse_package_file(root, changes):
    """Parse the package roots and append the metadata types to a dictionary."""
    for metadata_type in root.findall('sforce:types', ns):
        metadata_name = metadata_type.find('sforce:name', ns).text
        metadata_member_list = metadata_type.findall('sforce:members', ns)
        # If workflow child, determine Parent workflow and add to `Workflow` metadata type
        if metadata_name in WORKFLOW_CHILD_TYPES:
            changes.setdefault('Workflow', set()).update(metadata_member.text.split('.')[0] for metadata_member in metadata_member_list)
        # Otherwise, add metadata as-is to package unless there is a wildcard
        elif metadata_name and '*' not in metadata_name.strip():
            changes.setdefault(metadata_name, set()).update(metadata_member.text for metadata_member in metadata_member_list)
        elif '*' in metadata_name:
            logging.warning('WARNING: Wildcards are not allowed in the delta deployment package.')

    api_version = root.find('sforce:version', ns).text if root.find('sforce:version', ns) is not None else None
    return changes, api_version


def create_package_file(items, api_version, output_file):
    """Create the final package.xml file."""
    pkg_header = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    pkg_header += '<Package xmlns="http://soap.sforce.com/2006/04/metadata">\n'

    # if API version is provided, append to footer
    # otherwise, omit API version to use latest API version in org
    if api_version:
        pkg_footer = f'\t<version>{api_version}</version>\n</Package>\n'
    else:
        pkg_footer = '</Package>\n'

    # Initialize the package contents with the header
    package_contents = pkg_header

    # Append each item to the package
    for key in items:
        package_contents += "\t<types>\n"
        for member in items[key]:
            package_contents += "\t\t<members>" + member + "</members>\n"
        package_contents += "\t\t<name>" + key + "</name>\n"
        package_contents += "\t</types>\n"
    # Append the footer to the package
    package_contents += pkg_footer
    logging.info('Deployment package contents:')
    logging.info(package_contents)
    with open(output_file, 'w', encoding='utf-8') as package_file:
        package_file.write(package_contents)


def scan_package_metadata(package_path):
    """Scan the package and run the applicable scripts."""
    try:
        root = ET.parse(package_path).getroot()
    except ET.ParseError:
        logging.info('Unable to parse %s. Confirm XML is formatted correctly before re-trying.', package_path)
        sys.exit(1)

    package_labels = {}
    package_workflows = {}
    child_workflows = False

    for metadata_type in root.findall('sforce:types', ns):
        metadata_name = (metadata_type.find('sforce:name', ns)).text
        metadata_members = metadata_type.findall('sforce:members', ns)
        if metadata_name in INVALID_LABEL_TYPE:
            logging.info('ERROR: The metadata type `CustomLabels` (plural) is not allowed in delta deployments.')
            logging.info('Update the package.xml to use `CustomLabel` (singular) and declare specific labels to deploy.')
            sys.exit(1)
        if metadata_name in LABEL_TYPE:
            members = [member.text for member in metadata_members]
            package_labels = set_dictionary_members(members, package_labels)
        if metadata_name in WORKFLOW_PARENT_TYPE:
            members = [member.text for member in metadata_members]
            package_workflows = set_dictionary_members(members, package_workflows)
        if metadata_name in WORKFLOW_CHILD_TYPES:
            members = [member.text.split('.')[0] for member in metadata_members]
            package_workflows = set_dictionary_members(members, package_workflows)
            child_workflows = True

    if package_labels:
        combine_labels.combine_labels('force-app/main/default/labels',
                            'force-app/main/default/labels/CustomLabels.labels-meta.xml', True, package_labels)
    if package_workflows:
        combine_workflows.combine_workflows('force-app/main/default/workflows', True, package_workflows)
    # if the package has workflows, adjust the package automatically to comply with the known Salesforce CLI bug
    # For all workflow child items, find parent workflow and re-create package.xml with the parent workflow name
    if child_workflows:
        package_contents = {}
        logging.info('Adjusting the package.xml automatically to comply with Salesforce Workflow Deployments:')
        package_contents, api_version = parse_package_file(root, package_contents)
        create_package_file(package_contents, api_version, package_path)

def main(manifest):
    """Main function."""
    scan_package_metadata(manifest)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.manifest)
