# Trinity Hardware and Configuration Requirements

The Inchworm and Chrysalis steps can be memory intensive.  A basic recommendation is to have ~1G of RAM per ~1M pairs of Illumina reads. Simpler transcriptomes (lower eukaryotes) require less memory than more complex transcriptomes such as from vertebrates.  Trinity can also require hundreds of GB of disk space available and can generate many thousands of intermediate files during the run. However, the final output files generated are few and are often relatively small (MB rather than many GB). It's good to have a temporary workspace available with sufficient disk space to use during the job execution.

If you are able to run the entire Trinity process on a single high-memory multi-core server, indicate the number of butterfly processes to run in parallel by the --CPU parameter.   For more advanced installations leveraging massively parallel computing on LSF, SGE, UGE, SLURM, etc., see [documentation for parallelization on a compute farm](https://github.com/trinityrnaseq/trinityrnaseq/wiki/Running-Trinity#grid_conf).

Our experience is that the entire process can require ~1/2 hour to one hour per million pairs of reads in the current implementation (see link:[FAQ](Trinity-FAQ)).  We're striving to improve upon both memory and time requirements.

Unless you are running toy (test or tutorial) examples, you would be advised to run your Trinity job on a high performance server rather than a desktop or laptop personal computer.

If you do not have direct access to a high memory machine (typically having 256G or 512G of RAM), consider [running Trinity on one of the externally available resources](Accessing-Trinity-on-Publicly-Available-Compute-Resources).

