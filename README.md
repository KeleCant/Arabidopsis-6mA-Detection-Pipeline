# Arabidopsis 6mA/CpG Detection and Comparison Pipeline – Reproducibility Guide

### A note to the grader
This repository contains a reproducibility pipeline for our capstone project on 6mA and CpG methylation detection in Arabidopsis thaliana.

We understand that you are aware of the specific data-sharing constraints surrounding this project. Due to privacy and permission restrictions set by our sponsor and steward, we are not authorized to distribute the raw data files externally, including for grading purposes. This policy has been approved by Dr. Payne.

To support transparency and demonstrate our work, we have included:
- A detailed workflow guide
- An overview of expected inputs and processing steps
  
We are still working on making 6mA data presentable. In its current state, our pipeline gives an output for 6mA concentration but it is not accurate. Please be patient as we continue to work on this problem. Dr. Payne is aware of this hiccup.

Expected Inputs Files:
These are the files we would provide you with
  ```
  - 1000.bam (~12.3 GB)                 # Binary alignment file
  - 1000.bam.bai (~774 KB)              # BAM index file
  - arabidopsis.fasta (~115 MB)         # Reference genome
  - arabidopsis.fasta.fai (~195 bytes)  # FASTA index file
  ```

Expected Output Files:
  ```

  ```

Required tools:
| Tool | Purpose |
|-----------------|----------------------------|
| samtools | samtools is a suite of utilities for processing and analyzing .bam and .sam files. It is used to inspect aligned reads and verify the presence of methylation tags such as 6mA (A+a) or CpG (C+m) before running the full pipeline. |
| pbmm2 | pbmm2 is a PacBio-optimized alignment tool designed for mapping HiFi (CCS) reads to a reference genome. It is used to align unprocessed .bam files to the Arabidopsis thaliana reference, producing sorted and indexed BAM files. |
| Pb-cpg-tools |  |


### Step 1: Verify Presence of 6mA
Before executing the pipeline, it's important to confirm that N6-methyladenine (6mA) modifications are present in your .bam file. This step ensures that running the full analysis is justified.

  ```
  $ Samtools view [your_file.bam filename] | grep -c “A+a”
  ```
Example:
  ```
  $ samtools view 1000.bam | grep -c “A+a”
  ```

This command will return the number of reads in the .bam file that include the 6mA tag. 

Note: While it's not essential to verify the presence of CpG methylation, you can do so by replacing "A+a" with "C+m" in the command above:

  ```
  $ samtools view 1000.bam | grep -c "C+m"
  ```

### Step 2: Align 
Use pbmm2 to align your unprocessed .bam file to the reference genome. This generates a sorted and indexed .bam file for downstream analysis.

  ```
  $ pbmm2 align [genome file] [bam file] [output filename] --sort --preset CCS
  ```
Example:
  ```
  $ pbmm2 align arabidopsis.fasta 1000.bam 1000_mapped.bam --sort --preset CCS
  ```
Output: 1000_mapped.bam, 1000_mapped.bam.bai

(The index file [.bam.bai] is detected and inserted automatically)

### Step 3: Get CpG output
Pb-cpg-tools is a tool created by PacBio to create CpG (5mC) methylation probabilities using the .bam files created from pbmm2. Using the aligned_bam_to_cpg_scores command and a path the aligned .bam file (the .bai file must also be in the same directory) it will create multiple output files. The files we will use for further analysis and visualization are the .bw (bigwig) file and .bed file. 

### Step 4: Get 6mA output
convert.py is a simple python script written by our team to modify the .bed file from the previous into the format needed for further analysis. The new format of the file is a simplified .bed file containing only the necessary information.


### Step 5: Generate a Matrix
computeMatrix is a command included in deeptools, a command line tool available through bioconda. This is an intermediate step to compute a matrix that is used to generate a heatmap. The command requires the .bw (bigwig) file created by pb-cpg-tools and the new .bed file that was created by using convert.py. The additional arguments ensure that the genomic regions of interest are centered on the heatmap and the amount of basepairs on each side of the center point. The command will use the files and arguments to create a .MAT (matrix) file that will be used in the next step.


### Step 6: Plot Heatmap
plotHeatmap:
plotHeatmap is a command included in deeptools, a command line tool available through bioconda. This command uses the .MAT file from the previous step and creates a heatmap image file (png, svg, or pdf) based on the colors specified in the command.


### Step 6: View Data with Integrative Genomics Viewer (IGV)


