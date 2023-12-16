# Salesforce - Combine & Separate Custom Labels & Workflows

Salesforce tracks all custom labels in 1 file and all workflows for a single object in 1 file.

If you wish to separate labels and workflows into their own files for version control, run the separate scripts.

Run the combine scripts to re-combine labels and workflows into files compatible for deployments.

Use the provided `.gitignore` and `.forceignore` to have Git ignore the original meta files and have the Salesforce CLI ignore the separated XML files.

If you deploy all metadata in deployments, run the combine scripts directly without arguments to compile all labels and workflows in the default directories.

```
    - python3 ./combine_labels.py
    - python3 ./combine_workflows.py
```

If you deploy metadata declared in a manifest file, run the `parse_package.py` script to parse the package.xml and run the applicable scripts if custom labels or workflows are in the package.xml.

```
    - python3 ./parse_package.py --manifest "./manifest/package.xml"
```

At this time, manifest retrievals with the Salesforce CLI can use the children workflow metadata types like `WorkflowAlert`.

Manifest Deployments using workflow children types will have the following failure: `An object XXXXXXXX of type WorkflowAlert was named in package.xml, but was not found in zipped directory`.

The `parse_package.py` script will automatically adjust the package.xml to use the parent workflow if children workflow types are found in the package.

## Change-Log

December 15, 2023 - Combine Workflows script fixed to sort workflows similar to the Salesforce CLI. 

The issue `Error parsing file: Element fieldUpdates is duplicated at this location in type Workflow` was occuring again in CI pipelines due to the sorting of the workflows in the file.

The workflows created now resemble the CLI output. The above error has been resolved and the script is able to successfully deploy workflows in a CI pipeline.

December 16, 2023 - Add support for manifest/delta deployments to the combine scripts.
