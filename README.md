# AutoTrinity Pipeline

## Overview
AutoTrinity is an automated pipeline for transcriptome assembly, based on the pipeline outlined by the Harvard FAS informatics group here: https://web.archive.org/web/20221005185422/https://informatics.fas.harvard.edu/best-practices-for-de-novo-transcriptome-assembly-with-trinity.html


## Prerequisites
- Python 3
- BioPython
- Required tools installed in the `tools` directory:
  - FastQC
  - Rcorrector
  - TrimGalore
  - Trinity
  - Bowtie2
  - BUSCO
  - TransDecoder

## Installation
Clone the AutoTrinity repository:
```bash
git clone https://github.com/eastmountaincode/AutoTrinity.git
```

## Usage
To run the AutoTrinity pipeline, navigate to the directory containing the AutoTrinity.py script and execute the following command:
```
python3 AutoTrinity.py -i <folder_name>
```
Where `<folder_name>` is the name of the directory containing your input .fastq files.

## Input Files
Ensure that your input directory (`<folder_name>`) has the following files:

- `<folder_name>_1.fastq`: The first paired-end FASTQ file.
- `<folder_name>_2.fastq`: The second paired-end FASTQ file.

## Output
The output includes:

- Quality control reports.
- Corrected sequence reads.
- Trimmed FASTQ files.
- Alignment statistics.
- Assembled transcriptome in FASTA format. (at `/<input_folder>/trinity_out_dir/trinity_out_dir.Trinity.fasta`)
- ORF analysis (at `/<input_folder>/transdecoder_out/]`)
- High-level analytics including ORF counts and BUSCO completion rates.
- Logs of each step of the pipeline are written to `<input_folder>_AutoTrinity.log`, providing details on the execution status and any errors encountered. This is also where you will find the high-level analytics.

## High-Level Analytics
After pipeline execution, high-level analytics are generated, which include:

- Number of total and complete ORFs (Open Reading Frames).
- BUSCO (Benchmarking Universal Single-Copy Orthologs) completion rate.
- Overall alignment rate from Bowtie2.

## Author
Andrew Boylan

## License
MIT License

Copyright (c) 2024 Andrew Boylan

