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
  - arabidopsis.fasta (~115 MB)         # Reference genome in FASTA format
  - arabidopsis.fasta.fai (~195 bytes)  # Index file for the reference genome
  - RNA.fastq                           # Raw RNA sequencing data
  ```

Required tools:
| Tool | Purpose |
|-----------------|----------------------------|
| [samtools](https://github.com/samtools/samtools) | samtools is a set of utilities for processing and analyzing .bam and .sam files. It is used to inspect aligned reads and verify the presence of methylation tags such as 6mA (A+a) or CpG (C+m) before running the full pipeline. |
| [pbmm2](https://github.com/PacificBiosciences/pbmm2) | pbmm2 is a PacBio-optimized alignment tool designed for mapping HiFi (CCS) reads to a reference genome. It is used to align unprocessed .bam files to the Arabidopsis thaliana reference, producing sorted and indexed BAM files. |
| [Pb-cpg-tools](https://github.com/PacificBiosciences/pb-CpG-tools) | pb-CpG-tools is a PacBio utility for analyzing CpG methylation patterns from aligned HiFi sequencing data. It extracts and quantifies CpG methylation sites from .bam files, enabling downstream comparison of epigenetic modifications. |
| [deeptools](https://github.com/deeptools/deepTools) | deepTools is a collection of tools for analyzing and visualizing genomic data. It is used to generate a heatmap to analyze methylation data. |
| [modbam2bed](https://github.com/epi2me-labs/modbam2bed) | modbam2bed converts modified BAM files to the .bed format for easier analysis of methylation marks. This program fails to generate 6mA scores properly causing IGV graphs to look corrupted. This tool will likely be replaced with [Modkit](https://github.com/nanoporetech/modkit/?tab=readme-ov-file) or a handwritten Python script. |
| [bedGraphToBigWig](https://anaconda.org/bioconda/ucsc-bedgraphtobigwig) | bedGraphToBigWig is a utility for converting .bedGraph files to the .bigWig format. It is used to visualize genomic data in IGV, allowing for an efficient display of methylation. |


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

### Step 2: Align Reads with pbmm2
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

### Step 3A: Generate CpG Methylation Scores
pb-CpG-tools is a tool developed by PacBio to compute CpG (5mC) methylation probabilities from aligned HiFi .bam files. It requires that both the .bam and its corresponding .bai index file are present in the same directory.

Using the aligned_bam_to_cpg_scores command, the tool generates several output files. The key files used for downstream analysis and visualization are the .bed and .bw (BigWig) files.

  ```
  $ aligned_bam_to_cpg_scores --bam [aligned.bam]  --output-prefix [output_prefix]
  ```
Example:
  ```
  $ aligned_bam_to_cpg_scores --bam 1000_mapped.bam --output-prefix _CSS_Data
  ```
Output: 
  ```
  1000_mapped.combined.bed.gz      – A compressed BED file containing per-site CpG methylation probabilities across the genome
  1000_mapped.combined.bed.gz.tbi  – An index file for the BED, enabling fast lookup in genome browsers and tools
  1000_mapped.combined.bw          - A BigWig file for efficient visualization of methylation scores across the genome (e.g., in IGV or UCSC Genome Browser)
  1000_mapped.log                  - A log file capturing runtime information and any processing messages or errors
  ```

### Step 4A: Convert the bed file to a usable format
convert.py is a simple Python script written by our team to modify the .bed file from the previous into the format needed for further analysis. The new format of the file is a simplified .bed file containing only the necessary information.

First, unzip the bed file from the previous step.

  ```
  $ gunzip -c [bed.gz file] > [new .bed file]
  ```
Example:
  ```
  $ gunzip -c 1000_mapped.combined.bed.gz > 1000_mapped.combined.bed
  ```

Convert:
  ```
  $ python convert.py [input bed file] [output bed file]
  ```
  Example:
  ```
  $ python convert.py combined.bed new_bed.bed
  ```
Output: new_bed.bed

### Step 3B: Create 6mA bed file

```
$ modbam2bed -m 6mA updated_GCF_000001735.4_TAIR10.1_genomic.fasta 1007_mapped.bam > 1007_mapped.bed
```

```
$ awk '{ print $1"\t"$2"\t"$3"\t"$5 }' 1007_mapped.bed > 1007_mapped.bedgraph
```

### Step 4B: Convert 6mA bed file to .bw file

```
$ cut -f1,2 updated_GCF_000001735.4_TAIR10.1_genomic.fasta.fai > chrom.sizes
```

```
$ bedGraphToBigWig 1007_mapped.bedGraph chrom.sizes 1007_mapped.bw
```


### Step 5: Generate a Matrix
computeMatrix is a command included in deeptools, a command line tool available through bioconda. This is an intermediate step to compute a matrix that is used to generate a heatmap. The command requires the .bw (bigwig) file created by pb-cpg-tools and the new .bed file that was created by using convert.py. The additional arguments ensure that the genomic regions of interest are centered on the heatmap and the amount of basepairs on each side of the center point. The command will use the files and arguments to create a .MAT (matrix) file that will be used in the next step.

  ```
  $ computeMatrix reference-point --referencePoint center -bs binSize -a BP_after_BED -b BP_before_BED -p 4 -S  BIGWIGSofINTEREST --regionsFileName BEDFILEOFINTEREST --outFileName OUTFILE [filename.MAT]
  ```
Example 
  ```
  $ computeMatrix reference-point --referencePoint center -bs binSize -a BP_after_BED -b BP_before_BED -p 4 -S  BIGWIGSofINTEREST --regionsFileName BEDFILEOFINTEREST --outFileName OUTFILE [filename.MAT]
  ```


### Step 6: Plot Heatmap
plotHeatmap:
plotHeatmap is a command included in deeptools, a command line tool available through bioconda. This command uses the .MAT file from the previous step and creates a heatmap image file (png, svg, or pdf) based on the colors specified in the command.

  ```
  $ plotHeatmap -m MATRIXFILE -o HEATMAP --colorList lowColour, highColour
  ```
Example:
  ```
  $ plotHeatmap -m MATRIXFILE -o HEATMAP --colorList lowColour, highColour
  ```


### Step 7: View Data with Integrative Genomics Viewer (IGV)
1. Open Integrative Genomics Viewer (IGV) on your local computer. Select A. thaliana (TAIR 10) as the reference genome. This will open the RefSeq Genes as a track.
2. Locate the output aligned .bam and .bam.bai DNA files from pbmm2, the aligned RNA .bam and .bam.bai files, and the bigwig (.bw) file from the cpg-tool output. Ensure all of them are in the same directory.
3. In IGV open each .bam file to create 4 more tracks. This will produce a “Coverage” track and a reads track for both the DNA and RNA.
4. In IGV open the bigwig file as a track as well. At this point you will have a total of 6 tracks.
5. In the top section of IGV there is a place to type in the region of interest and zoom in. Enter the region you would like to examine (the one in the figure is on chromosome 5 from nucleotide 8,647,136 to nucleotide 8,651,646).
6. On the left hand side of the window there will be labels for each track. Right click on the DNA_file_name.bam track and remove that track. Do the same thing for the RNA_file_name.bam track. This will leave you with the bigwig track, DNA coverage track, RNA coverage track, and RefSeq Genes track (ie the figure). 

