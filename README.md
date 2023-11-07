# Salesforce - Combine & Separate Custom Labels & Workflows

Salesforce tracks all custom labels in 1 file and all workflows for a single object in 1 file.

If you wish to separate labels and workflows into their own files for version control, run the separate scripts.

Run the combine scripts to re-combine labels and workflows into files compatible for deployments.

Use the provided `.gitignore` and `.forceignore` to have Git ignore the original meta files and have the Salesforce CLI ignore the separated XML files.

The package parsing script can be used to run the scripts only when labels or workflow metadata types are declared in the manifest file.

## Custom Label Process 

Seed the repository by retrieving all labels from production using `CustomLabels` and then running the separate script.

To add/update labels:
1. Retrieve specific labels with `CustomLabel`
2. Run the separate script to create/update separate XMLs for each label
3. Update your deployment process to run the combine script to combine all labels during label deployments

## Workflow Process 

Seed the repository by retrieving all workflows from production using `Workflow` and then running the separate script.

To add/update workflows:
1. Retrieve all workflows for an object with `Workflow` or retrieve specific workflow actions using the children metadata types like `WorkflowAlert`
2. Run the separate script to create/update separate XMLs for each workflow
3. Update your deployment process to run the combine script to combine all workflows during workflow deployments
     1. At this time, retrievals with the Salesforce CLI can use the children metadata types like `WorkflowAlert`
     2. Deployments using children types like `WorkflowAlert` will have the following failure: `An object XXXXXXXX of type WorkflowAlert was named in package.xml, but was not found in zipped directory`
     3. Deployments must use the parent `Workflow` type, but this approach will provide greater version control over specific workflow actions you do not want to accidentally overwrite
