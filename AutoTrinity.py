#!/usr/bin/env python3

import argparse
import os
import subprocess
from datetime import datetime

class AutoTrinity:
    def __init__(self, dir_name):
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.dir_name = dir_name
        self.output_dir = dir_name
        self.log_file = os.path.join(self.output_dir, f"{dir_name}_AutoTrinity.log")
        self.fastq_file_1_path = os.path.join(self.output_dir, f"{dir_name}_1.fastq")
        self.fastq_file_2_path = os.path.join(self.output_dir, f"{dir_name}_2.fastq")
        self._check_directory_and_files()
        self._init_log()
        self.tools_dir = os.path.join(self.script_dir, "tools")

    def _check_directory_and_files(self):
        if not os.path.isdir(self.output_dir):
            raise FileNotFoundError(f"The directory '{self.output_dir}' does not exist.")

        if not os.path.isfile(self.fastq_file_1_path) or not os.path.isfile(self.fastq_file_2_path):
            raise FileNotFoundError(f"Required FASTQ files not found in '{self.output_dir}'.")

    def _init_log(self):
        with open(self.log_file, 'w') as log:
            log.write(f"{self._get_current_timestamp()} -- Initialize AutoTrinity Pipeline Log\n")

    def _get_current_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log(self, message):
        with open(self.log_file, 'a') as log:
            log.write(f"{self._get_current_timestamp()} -- {message}\n")

    def run_command(self, command):
        self.log(f"Running command: {command}")
        try:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            self.log(f"Error in command {command}: {str(e)}")
            raise

    def fastqc_analysis_pre(self):
        fastqc_path = os.path.join(self.tools_dir, "FastQC", "fastqc")
        fastqc_output_dir = os.path.join(self.output_dir, "preprocessed_fastqc")

        # Create the fastqc_output_dir if it doesn't exist
        if not os.path.exists(fastqc_output_dir):
            os.makedirs(fastqc_output_dir)

        command_1 = f"{fastqc_path} {self.fastq_file_1_path} -o {fastqc_output_dir}"
        command_2 = f"{fastqc_path} {self.fastq_file_2_path} -o {fastqc_output_dir}"
        self.run_command(command_1)
        self.run_command(command_2)
        self.log("FASTQC analysis completed.")

    def remove_erroneous_kmers(self):
        rcorrector_path = os.path.join(self.script_dir, "tools", "Rcorrector", "run_rcorrector.pl")
        corrected_output_dir = self.output_dir

        # Construct the command
        command = f"perl {rcorrector_path} -t 32 -1 {self.fastq_file_1_path} -2 {self.fastq_file_2_path} -od {corrected_output_dir}"
        self.run_command(command)
        self.log("Erroneous k-mer removal completed (rcorrector).")

    def discard_unfixable_read_pairs(self):
        discard_script_path = os.path.join(self.tools_dir, "DiscardUnfixable.py")
        corrected_fastq_1 = os.path.join(self.output_dir, f"{self.dir_name}_1.cor.fq")
        corrected_fastq_2 = os.path.join(self.output_dir, f"{self.dir_name}_2.cor.fq")

        # Run the DiscardUnfixable.py script
        command = f"python3 {discard_script_path} -1 {corrected_fastq_1} -2 {corrected_fastq_2} -s {self.dir_name}"
        self.run_command(command)
        self.log("Discarding unfixable read pairs completed (DiscardUnfixable.py).")

    def trim_adapters_and_low_quality_bases(self):
        trim_galore_path = os.path.join(self.tools_dir, "TrimGalore-0.6.10", "trim_galore")
        input_fastq_1 = os.path.join(self.output_dir, f"unfixrm_{self.dir_name}_1.cor.fq")
        input_fastq_2 = os.path.join(self.output_dir, f"unfixrm_{self.dir_name}_2.cor.fq")

        # Run TrimGalore
        command = f"{trim_galore_path} --paired --retain_unpaired --phred33 --output_dir {self.output_dir} --length 36 -q 5 --stringency 1 -e 0.1 {input_fastq_1} {input_fastq_2}"
        self.run_command(command)
        self.log("Trimming of adapters and low-quality bases completed.")


    def execute_pipeline(self):
        self.log("Starting the AutoTrinity Pipeline.")
        #self.fastqc_analysis_pre()
        #self.remove_erroneous_kmers()
        #self.discard_unfixable_read_pairs()
        self.log("AutoTrinity Pipeline completed.")

def main():
    parser = argparse.ArgumentParser(description='AutoTrinity: An Automated Transcriptome Assembly Pipeline')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input directory name')
    parser.add_argument('-v', '--version', action='version', version='AutoTrinity Pipeline v0.1')
    args = parser.parse_args()

    try:
        autotrinity = AutoTrinity(args.input)
        autotrinity.execute_pipeline()
    except FileNotFoundError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

