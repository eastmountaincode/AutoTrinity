#!/usr/bin/env python3

import argparse
import os
import subprocess
from datetime import datetime
import shutil

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
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            self.log(f"Error in command {command}: {str(e)}")
            raise

    def verify_required_tools(self):
        required_tools = {
            'FastQC': {'path': os.path.join(self.tools_dir, "FastQC", "fastqc"), 'test_command': '--version'},
            'Rcorrector': {'path': os.path.join(self.tools_dir, "Rcorrector", "run_rcorrector.pl"), 'test_command': '-version', 'interpreter': 'perl'},
            'TrimGalore': {'path': os.path.join(self.tools_dir, "TrimGalore-0.6.10", "trim_galore"), 'test_command': '--version'},
            'Trinity': {'path': os.path.join(self.tools_dir, "trinityrnaseq-v2.15.1", "Trinity"), 'test_command': '--version'},
            'Bowtie2': {'path': os.path.join(self.tools_dir, "bowtie2-2.5.2", "bowtie2"), 'test_command': '--version'},
            'BUSCO': {'path': os.path.join(self.tools_dir, "busco-5.5.0", "src", "busco", "run_BUSCO.py"), 'test_command': '--version'},
            'TransDecoder_LongOrfs': {'path': os.path.join(self.tools_dir, "TransDecoder", "TransDecoder.LongOrfs"), 'test_command': '--version'},
            'TransDecoder_Predict': {'path': os.path.join(self.tools_dir, "TransDecoder", "TransDecoder.Predict"), 'test_command': '--version'}
        }

        for tool_name, tool_info in required_tools.items():
            if not os.path.isfile(tool_info['path']):
                raise FileNotFoundError(f"Required tool '{tool_name}' not found at '{tool_info['path']}'.")

            command = []
            if 'interpreter' in tool_info:  # Check if 'interpreter' key exists
                command.append(tool_info['interpreter'])
            command.append(tool_info['path'])
            command.append(tool_info['test_command'])

            try:
                subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError:
                raise EnvironmentError(f"Tool '{tool_name}' at '{tool_info['path']}' cannot be executed. Please check installation.")
 


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

    def fastqc_analysis_post(self):
        fastqc_path = os.path.join(self.tools_dir, "FastQC", "fastqc")
        fastqc_output_dir = os.path.join(self.output_dir, "postprocessed_fastqc")

        # Create the fastqc_output_dir if it doesn't exist
        if not os.path.exists(fastqc_output_dir):
            os.makedirs(fastqc_output_dir)

        processed_fastq_1 = os.path.join(self.output_dir, f"unfixrm_{self.dir_name}_1.cor_val_1.fq")
        processed_fastq_2 = os.path.join(self.output_dir, f"unfixrm_{self.dir_name}_2.cor_val_2.fq")

        # Run FastQC on post-processed FASTQ files
        command_1 = f"{fastqc_path} {processed_fastq_1} -o {fastqc_output_dir}"
        command_2 = f"{fastqc_path} {processed_fastq_2} -o {fastqc_output_dir}"
        self.run_command(command_1)
        self.run_command(command_2)
        self.log("FastQC analysis on post-processed reads completed.")

    def assemble_transcriptome_with_trinity(self):
        trinity_path = os.path.join(self.tools_dir, "trinityrnaseq-v2.15.1", "Trinity")
        left_input = os.path.join(self.output_dir, f"unfixrm_{self.dir_name}_1.cor_val_1.fq")
        right_input = os.path.join(self.output_dir, f"unfixrm_{self.dir_name}_2.cor_val_2.fq")
        trinity_output_dir = os.path.join(self.output_dir, "trinity_out_dir")

        # Run Trinity
        command = f"{trinity_path} --seqType fq --left {left_input} --right {right_input} --CPU 32 --max_memory 100G --output {trinity_output_dir}"
        self.run_command(command)
        self.log("Transcriptome assembly with Trinity completed.")

        # Move the Trinity output files
        #for file in os.listdir(trinity_output_dir):
        #    if file.startswith("Trinity"):
        #        shutil.move(os.path.join(trinity_output_dir, file), self.output_dir)

    def move_trinity_files(self):
        trinity_output_dir = os.path.join(self.output_dir, "trinity_out_dir")
        # Move the Trinity output files and directories
        for item in os.listdir(self.output_dir):
            if "Trinity" in item and "AutoTrinity" not in item:
                source_path = os.path.join(self.output_dir, item)
                dest_path = os.path.join(trinity_output_dir, item)

                if os.path.isdir(source_path):
                    shutil.move(source_path, dest_path)
                elif os.path.isfile(source_path):
                    shutil.move(source_path, dest_path)

    def generate_alignment_summary_metrics(self):
        trinity_stats_script = os.path.join(self.tools_dir, "trinityrnaseq-v2.15.1", "util", "TrinityStats.pl")
        trinity_fasta = os.path.join(self.output_dir, "trinity_out_dir", "trinity_out_dir.Trinity.fasta")
        stats_output = os.path.join(self.output_dir, f"{self.dir_name}_trinity_stats.metrics")

        # Run TrinityStats.pl and redirect output to a file
        command = f"perl {trinity_stats_script} {trinity_fasta} > {stats_output}"
        self.run_command(command)
        self.log("Basic alignment summary metrics generated.")


    def bowtie_build_index(self):
        trinity_fasta = os.path.join(self.output_dir, "trinity_out_dir", "trinity_out_dir.Trinity.fasta")

        # Specify the output directory for the Bowtie index
        bowtie_index_dir = os.path.join(self.output_dir, "bowtie_index")
        os.makedirs(bowtie_index_dir, exist_ok=True)
        bowtie_index_prefix = os.path.join(bowtie_index_dir, "trinity_index")

        bowtie_build_path = os.path.join(self.tools_dir, "bowtie2-2.5.2", "bowtie2-build")
        bowtie_build_command = f"{bowtie_build_path} --threads 16 {trinity_fasta} {bowtie_index_prefix}"
        
        # Run bowtie2-build
        self.run_command(bowtie_build_command)
        self.log(f"bowtie2-build --threads 16 {trinity_fasta} {bowtie_index_prefix}")

    def run_bowtie2_alignment(self):
        bowtie2_path = os.path.join(self.tools_dir, "bowtie2-2.5.2", "bowtie2")
        bowtie_index_prefix = os.path.join(self.output_dir, "bowtie_index", "trinity_index")
        left_input = os.path.join(self.output_dir, f"unfixrm_{self.dir_name}_1.cor_val_1.fq")
        right_input = os.path.join(self.output_dir, f"unfixrm_{self.dir_name}_2.cor_val_2.fq")

        bowtie_output_dir = os.path.join(self.dir_name, "bowtie_output")
        os.makedirs(bowtie_output_dir, exist_ok=True)

        align_stats_file = os.path.join(bowtie_output_dir, f"{self.dir_name}_align_stats.txt")
        sam_output_file = os.path.join(bowtie_output_dir, f"{self.dir_name}_SAM_output.txt")
        bowtie_align_summary = os.path.join(bowtie_output_dir, f"{self.dir_name}_bowtie_align_summary.txt")

        # Run bowtie2 alignment
        with open(bowtie_align_summary, 'w') as summary_file:
            bowtie_command = f"{bowtie2_path} -p 25 -q --no-unal -k 20 -x {bowtie_index_prefix} -1 {left_input} -2 {right_input} --met-file {align_stats_file} -S {sam_output_file}"
            subprocess.run(bowtie_command, shell=True, check=True, stdout=summary_file, stderr=subprocess.STDOUT)
        
        self.log("Bowtie2 alignment completed.")

    def run_busco_analysis(self):
        # Path to the run_BUSCO.py script
        busco_script_path = os.path.join(self.tools_dir, "busco-5.5.0", "src", "busco", "run_BUSCO.py")

        # Path to the input file (Trinity.fasta) and BUSCO output directory
        trinity_fasta = os.path.join(self.output_dir, "trinity_out_dir", "trinity_out_dir.Trinity.fasta")
        busco_output_dir = os.path.join(self.output_dir, "busco_output")
        busco_lineages_path = "eukaryota_odb10"

        # Construct the BUSCO command
        busco_command = f"python3 {busco_script_path} -c 16 -o {busco_output_dir} -i {trinity_fasta} -l {busco_lineages_path} -m transcriptome"

        # Run BUSCO
        self.run_command(busco_command)
        self.log("BUSCO analysis completed.")

    def transdecoder_longorfs(self):
        # Path to the TransDecoder.LongOrfs script
        transdecoder_longorfs_path = os.path.join(self.tools_dir, "TransDecoder", "TransDecoder.LongOrfs")
        trinity_fasta = os.path.join(self.output_dir, "trinity_out_dir", "trinity_out_dir.Trinity.fasta")

        transdecoder_out = os.path.join(self.dir_name, "transdecoder_out")
        os.makedirs(transdecoder_out, exist_ok=True)

        # Construct and run the TransDecoder.LongOrfs command
        longorfs_command = f"{transdecoder_longorfs_path} -t {trinity_fasta} --output_dir {transdecoder_out}"
        self.run_command(longorfs_command)
        self.log("TransDecoder LongOrfs analysis completed.")

    def transdecoder_predict(self):
        # Path to the TransDecoder.Predict script
        transdecoder_predict_path = os.path.join(self.tools_dir, "TransDecoder", "TransDecoder.Predict")
        trinity_fasta = os.path.join(self.output_dir, "trinity_out_dir", "trinity_out_dir.Trinity.fasta")

        transdecoder_out = os.path.join(self.dir_name, "transdecoder_out")

        # Construct and run the TransDecoder.Predict command
        predict_command = f"{transdecoder_predict_path} -t {trinity_fasta} --output_dir {transdecoder_out}"
        self.run_command(predict_command)
        self.log("TransDecoder Predict analysis completed.")


    def execute_pipeline(self):
        #self.log("Starting the AutoTrinity Pipeline.")
        self.verify_required_tools()
        #self.fastqc_analysis_pre()
        #self.remove_erroneous_kmers()
        #self.discard_unfixable_read_pairs()
        #self.trim_adapters_and_low_quality_bases()
        #self.fastqc_analysis_post()
        #self.assemble_transcriptome_with_trinity()
        #self.move_trinity_files()
        #self.generate_alignment_summary_metrics()
        #self.bowtie_build_index()
        #self.run_bowtie2_alignment()
        #self.run_busco_analysis()
        #self.transdecoder_longorfs()
        #self.transdecoder_predict()
        #self.log("AutoTrinity Pipeline completed.")

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

