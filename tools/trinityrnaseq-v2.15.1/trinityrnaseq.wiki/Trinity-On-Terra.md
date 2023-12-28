# Terra

Instructions for running Trinity on [Terra](https://app.terra.bio/#workspaces/ctat-firecloud/Trinity). The Trinity workflow is available [here](https://portal.firecloud.org/#methods/CTAT/trinityrnaseq/).

1.  Upload your FASTQ files to your workspace bucket.
    > Example:
    > 
    >     gsutil -m cp /foo/bar/projects/*.fastq.gz gs://my-bucket/

    Please see [here](https://support.terra.bio/hc/en-us/articles/360024056512-Uploading-to-a-workspace-Google-bucket) for additional documentation.

1.  Import *CTAT/trinityrnaseq* workflow to your workspace.
    > See the Terra documentation for [adding a workflow](https://support.terra.bio/hc/en-us/articles/360025674392-Finding-the-workflow-method-you-need-in-the-Methods-Repository). 


1.  In your workspace, open `trinityrnaseq` in the `WORKFLOWS` tab. 
    If you are running a single sample, select
    `Run workflow with inputs defined by file paths`, otherwise select `Run workflow(s) with inputs defined by data table`.
    Terra uses a [workspace data table](https://support.terra.bio/hc/en-us/articles/360025758392) to run a workflow over multiple samples.
    Enter the workflow parameters and and click the `Save` button. 
-----

## Inputs

Please see the description of important inputs below.


| Name           | Description | Example Value
| -------------- | ----------- | ----------- |
| left           | Array of left FASTQ files | ["gs://my-bucket/10M.left.fq.gz"] |
| right          | Array of right FASTQ files | ["gs://my-bucket//10M.right.fq.gz"] |
| genome_guided_bam | BAM file for genome guided assembly | "gs://my-bucket//aligned.bam" 
| extra_args     | Extra command line arguments to pass to Trinity | "--seqType fq --SS_lib_type RF" |
| memory_read_clustering_phase          | Memory for read clustering phase (default 150G) | "25G" |


## Outputs

| File        | Description |
| ----------- | ----------- |
| Trinity.fasta  | Trinity assembly FASTA |
| Trinity.fasta.gene_trans_map  | File that maps gene to transcripts |
