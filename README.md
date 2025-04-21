# Arabidopsis 6mA/CpG Detection and Comparison Pipeline
This project is part of a Bioinformatics capstone conducted in collaboration with the BYU Genetics Lab. Our objective is to investigate and compare the presence of N6-methyladenine (6mA) in Arabidopsis thaliana alongside 5-methylcytosine (5mC) methylation patterns. Due to privacy considerations and restrictions imposed by our project sponsor and data steward, we are not authorized to distribute the raw data files externally.

# Reproducibility Guide
Expected Input Files:
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
| [pb-cpg-tools](https://github.com/PacificBiosciences/pb-CpG-tools) | pb-CpG-tools is a PacBio utility for analyzing CpG methylation patterns from aligned HiFi sequencing data. It extracts and quantifies CpG methylation sites from .bam files, enabling downstream comparison of epigenetic modifications. |
| [bedGraphToBigWig](https://anaconda.org/bioconda/ucsc-bedgraphtobigwig) | bedGraphToBigWig is a utility for converting .bedGraph files to the .bigWig format. It is used to visualize genomic data in IGV, allowing for an efficient display of methylation. |
| [deeptools](https://github.com/deeptools/deepTools) | deepTools is a collection of tools for analyzing and visualizing genomic data. It is used to generate a heatmap to analyze methylation data. |

### Software Installation Instructions:
There are several ways to set up the required tools for this pipeline. The recommended and most straightforward method is via Docker; Docker will install all required programs so you can run through each command of the pipeline. A comprehensive setup guide is available [here](https://github.com/KeleCant/Arabidopsis-6mA-Detection-Pipeline/blob/main/Docker%20Setup.md).

Alternatively, users may choose to configure a Conda environment or utilize Nextflow. These approaches require manual installation of each tool. Both tools are available via Docker.

For users operating on the BYU supercomputer, most tools can be accessed using the module load command, except for pb-cpg-tools, which is not currently available as a module. To use pb-cpg-tools, you will need to reference its direct path and invoke it as a function. For example, if you are on the BYU Super Computer for the Genetics lab in the Capstone directory use:
```
2_software/Pb-6mA-tool/pb-CpG-tools-v3.0.0-x86_64-unknown-linux-gnu/bin/aligned_bam_to_cpg_scores
```
Example usage of module loading:
```
module load <tool_name>
```

### Step 1: Verify Presence of 6mA
Before executing the pipeline, it's important to confirm that N6-methyladenine (6mA) modifications are present in your .bam file. This step ensures that running the full analysis is justified.

  ```
  $ samtools view [your_file.bam filename] | grep -c "A+a"
  ```
Example:
  ```
  $ samtools view 1000.bam | grep -c "A+a"
  ```

This command will return the number of reads in the .bam file that include the 6mA tag. 

Note: While it's not essential to verify the presence of CpG methylation, you can do so by replacing "A+a" with "C+m" in the command above:

  ```
  $ samtools view 1000.bam | grep -c "C+m"
  ```


### Step 2: Align Reads with pbmm2
Use pbmm2, a PacBio-optimized aligner, to map both your unprocessed .bam file and RNA sequencing data to the reference genome. This generates a sorted and indexed .bam file for downstream analysis.

  ```
  $ pbmm2 align [genome file] [bam file] [output filename] --sort --preset CCS
  ```
Example:
  ```
  $ pbmm2 align arabidopsis.fasta 1000.bam 1000_mapped.bam --sort --preset CCS
  ```
Output: 1000_mapped.bam, 1000_mapped.bam.bai

(The index file [.bam.bai] is detected and inserted automatically)

## Steps 3 and 4 have two scripts that run in parallel to each other in Nextflow. A is for CpG, and B is for 6mA. Both generate the same type of outputs.

### Step 3A: Generate CpG Methylation Scores
pb-CpG-tools is a tool developed by PacBio to compute CpG (5mC) methylation probabilities from aligned HiFi .bam files. It requires that both the .bam and its corresponding .bai index file are present in the same directory.

Using the aligned_bam_to_cpg_scores command, the tool generates several output files. The key files used for downstream analysis and visualization are the .bed and .bw (BigWig) files.

  ```
  $ aligned_bam_to_cpg_scores --bam [aligned.bam] --output-prefix [output Name]
  ```
Example:
  ```
  $ aligned_bam_to_cpg_scores --bam 1000_mapped.bam --output-prefix 1000_mapped
  ```
Output: 
  ```
  1000_mapped.combined.bed.gz      – A compressed BED file containing per-site CpG methylation probabilities across the genome
  1000_mapped.combined.bed.gz.tbi  – An index file for the BED, enabling fast lookup in genome browsers and tools
  1000_mapped.combined.bw          - A BigWig file for efficient visualization of methylation scores across the genome (e.g., in IGV or UCSC Genome Browser)
  1000_mapped.log                  - A log file capturing runtime information and any processing messages or errors
  ```


### Step 4A: Convert the BED File to a Usable Format
convert.py is a custom Python script developed by our team to reformat the .bed file from the previous step into a simplified format suitable for further analysis. This new .bed file contains only the necessary data for further processing.

**Unzip the BED file:**
Before conversion, you’ll need to unzip the .bed.gz file from step 3A.
  ```
  $ gunzip -c [input.bed.gz file] > [output.bed file]
  ```
Example:
  ```
  $ gunzip -c 1000_mapped.combined.bed.gz > 1000_mapped.combined.bed
  ```


**Convert the file format:**
Run the convert.py script to transform the .bed file into the new format.
  ```
  $ python convert.py [input bed file] [output bed file]
  ```
  Example:
  ```
  $ python convert.py 1000_mapped.combined.bed 1000_mapped_updated.bed
  ```
Output: 1000_mapped_updated.bed


### Step 3B: Create a 6mA BED File
Convert .bam file into a .sam file format for python script
```
$ samtools view -h 1000_mapped.bam | head > 1000_mapped.sam
```

Next run the Python script
```
python CpG_to_6mA_Script.py 1007_mapped.sam
```

### Step 4B: Convert 6mA BED File to .bw File
**Extract Chromosome Data**
To create a .bw (BigWig) file, first extract chromosome sizes from the reference genome's .fai index file.
  ```
  $ cut -f1,2 [reference_genome.fasta.fai] > chrom.sizes
  ```
Example:
  ```
  $ cut -f1,2 arabidopsis.fasta.fai > chrom.sizes
  ```

**Create BigWig File**
Next, use bedGraphToBigWig to convert the .bed file into a .bw file for IGV visualization.
  ```
  $ bedGraphToBigWig [input.bedGraph] [chrom.sizes] [output.bw]
  ```
Example:
  ```
  $ bedGraphToBigWig 1000_mapped_6mA.bed chrom.sizes 1000_mapped_6mA.bw
  ```


### Step 5: Generate a Matrix
computeMatrix is a command from deeptools, a tool available through Bioconda, used to compute a matrix for generating a heatmap. This step requires the .bw (BigWig) file created by pb-cpg-tools and the .bed file generated using convert.py. The command centers the genomic regions of interest and defines the number of base pairs on each side of the center. The output is a .MAT (matrix) file, which will be used in the next step.

  ```
  $ computeMatrix reference-point --referencePoint center -bs [binSize] -a [BP_after_BED] -b [BP_before_BED] -p 4 -S [BIGWIGSofINTEREST] --regionsFileName [BEDFILEOFINTEREST] --outFileName [filename.MAT]
  ```
Example 
  ```
  $ computeMatrix reference-point --referencePoint center -bs 50 -a 500 -b 500 -p 4 -S 1000_mapped.combined.bw --regionsFileName 1000_mapped_updated.bed --outFileName matrix.MAT
  ```


### Step 6: Plot [Heatmap](https://github.com/KeleCant/Arabidopsis-6mA-Detection-Pipeline/blob/main/Figure%203.pdf)
plotHeatmap is a command from deeptools, available through Bioconda, that generates a heatmap image from the .MAT matrix file created in the previous step. The command allows you to customize the color scheme for the heatmap and output the result in different formats, such as PNG, SVG, or PDF.

  ```
  $ plotHeatmap -m [MATRIXFILE] -o [HEATMAP] --colorList [lowColour, highColour]
  ```
Example:
  ```
  $ plotHeatmap -m matirix.MAT -o heatmap.png --colorList white,darkred
  ```


### Step 7: View Data with [Integrative Genomics Viewer (IGV)](https://github.com/KeleCant/Arabidopsis-6mA-Detection-Pipeline/blob/main/Figure%201.pdf)
1. Download [IGV](https://igv.org/download/html/oldtempfixForDownload.html)
1. Open Integrative Genomics Viewer (IGV) on your local computer. Select A. thaliana (TAIR 10) as the reference genome. This will open the RefSeq Genes as a track.
2. Locate the output aligned .bam and .bam.bai DNA files from pbmm2, the aligned RNA .bam and .bam.bai files, and the bigwig (.bw) file from the cpg-tool output. Ensure all of them are in the same directory.
3. In IGV open each .bam file to create 4 more tracks. This will produce a “Coverage” track and a reads track for both the DNA and RNA.
4. In IGV open the bigwig file as a track as well. At this point you will have a total of 6 tracks.
5. In the top section of IGV there is a place to type in the region of interest and zoom in. Enter the region you would like to examine (the one in the figure is on chromosome 5 from nucleotide 8,647,136 to nucleotide 8,651,646).
6. On the left hand side of the window there will be labels for each track. Right click on the DNA_file_name.bam track and remove that track. Do the same thing for the RNA_file_name.bam track. This will leave you with the bigwig track, DNA coverage track, RNA coverage track, and RefSeq Genes track (ie the figure). 

