import argparse
import logging
import sys
import xml.etree.ElementTree as ET

from combine_labels import create_combined_label_file
from combine_workflows import combine_workflows

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
ns = {'sforce': 'http://soap.sforce.com/2006/04/metadata'}


def parse_args():
    """
        Function to parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='A script to scan the package.')
    parser.add_argument('-m', '--manifest', default='manifest/package.xml')
    args = parser.parse_args()
    return args


def scan_package_metadata(package_path):
    """
        Function to check package for custom labels and workflows.
    """
    try:
        root = ET.parse(package_path).getroot()
    except ET.ParseError:
        logging.info('Unable to parse %s. Confirm XML is formatted correctly before re-trying.', package_path)
        sys.exit(1)

    label_types = ['CustomLabel', 'CustomLabels']
    workflow_types = ['Workflow', 'WorkflowAlert', 'WorkflowFieldUpdate', 'WorkflowFlowAction', 'WorkflowKnowledgePublish', 'WorkflowOutboundMessage', 'WorkflowRule', 'WorkflowTask']
    labels_created = False
    workflows_created = False

    for metadata_type in root.findall('sforce:types', ns):
        metadata_name = (metadata_type.find('sforce:name', ns)).text
        if metadata_name in label_types and labels_created is False:
            create_combined_label_file('force-app/main/default/labels',
                                       'force-app/main/default/labels/CustomLabels.labels-meta.xml')
            labels_created = True
        if metadata_name in workflow_types and workflows_created is False:
            combine_workflows('force-app/main/default/workflows')
            workflows_created = True


def main(manifest):
    """
    Main function to run the script.
    """
    scan_package_metadata(manifest)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.manifest)
