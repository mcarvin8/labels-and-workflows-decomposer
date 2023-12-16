# Salesforce - Combine & Separate Custom Labels & Workflows

Salesforce tracks all custom labels in 1 file and all workflows for a single object in 1 file.

If you wish to separate labels and workflows into their own files for version control, run the separate scripts.

Run the combine scripts to re-combine labels and workflows into files compatible for deployments.

Use the provided `.gitignore` and `.forceignore` to have Git ignore the original meta files and have the Salesforce CLI ignore the separated XML files.

The package parsing script can be used to run the scripts only when labels or workflow metadata types are declared in the manifest file.

If you deploy all metadata in all deployments, omit the `--manifest` argument in the combine scripts to compile all labels and workflows for the deployment.

```
    - python3 ./combine_labels.py
    - python3 ./combine_workflows.py
```

If you deploy metadata declared in a manifest file, run the `parse_package.py` script to parse the package.xml and run the combine scripts if `CustomLabel` or `Workflow` is in the package. This script will supply the `--manifest` argument and an additional argument containing the labels and workflows listed in the package.xml.

At this time, retrievals with the Salesforce CLI can use the children metadata types like `WorkflowAlert`.

Deployments using children types like `WorkflowAlert` will have the following failure: `An object XXXXXXXX of type WorkflowAlert was named in package.xml, but was not found in zipped directory`.

The `parse_package.py` script will automatically adjust the package.xml to list the parent workflow if children workflow types are found in the package.

## Change-Log

December 15, 2023 - Combine Workflows script fixed to sort workflows similar to the Salesforce CLI. 

The issue `Error parsing file: Element fieldUpdates is duplicated at this location in type Workflow` was occuring again in CI pipelines due to the sorting of the workflows in the file.

The workflows created now resemble the CLI output. The above error has been resolved and the script is able to successfully deploy workflows in a CI pipeline.

December 16, 2023 - Add support for manifest/delta deployments to the combine scripts.
