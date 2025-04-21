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
Convert the .bam file to .sam format for compatibility with the Python analysis script:
```
$ samtools view -h 1000_mapped.bam | head > 1000_mapped.sam
```
Run the 6mA BED generation script:
```
python Gen_6mA_beds.py 1000_mapped.sam
```
Output:
```
1000_mapped_6mA_pos.bed
1000_mapped_6mA_pos.bed
```

**Alternative Approach**: Multistrand 6mA Detection
PacBio provides two approaches to detect 6mA methylation: single-strand and multistrand analysis. This pipeline uses the multistrand method, which increases sensitivity by examining methylation marks on both positive and negative DNA strands.

- On the primary strand, methylation is detected via the "A+a" tag.

- On the complementary strand, it is inferred from the "T-a" tag.

These tags represent methylated adenosine residues (6mA). By accounting for both strands, this method typically yields approximately twice the number of 6mA sites compared to single-strand analysis.

Run the multistrand-aware script:
  ```
  python Gen_6mA_beds_T.py 1000_mapped.sam
  ```
Output:
  ```
  1000_mapped_6mA_T_pos.bed
  1000_mapped_6mA_T_pos.bed
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


### Step 5: Generate a Signal Matrix for Heatmap Visualization
The computeMatrix tool from the deepTools suite is used to prepare a matrix of signal values for visualization (e.g., via heatmaps or profile plots). This matrix aggregates methylation signals from a BigWig (.bw) file across specified genomic regions from a BED file, centering the analysis around a defined reference point (e.g., region center).
Input:
  ```
  - BigWig file (.bw): Contains genome-wide methylation signal data, typically generated by pb-cpg-tools.
  - BED file (.bed): Contains genomic regions of interest, generated using convert.py.
  - Reference point: The center of each BED region will be used for alignment.
  ```

  ```
  $ computeMatrix reference-point --referencePoint center -bs [binSize] -a [BP_after_BED] -b [BP_before_BED] -p 4 -S [BIGWIGSofINTEREST] --regionsFileName [BEDFILEOFINTEREST] --outFileName [filename.MAT]
  ```
- -bs: Bin size (in base pairs) for summarizing the signal.
- -a: Distance downstream (after) the center to include in the matrix.
- -b: Distance upstream (before) the center to include.
- -p: Number of processing threads.
- -S: BigWig file(s) containing signal data.
- --regionsFileName: BED file with target regions.
- --outFileName: Name of the output matrix file (used in Step 6).

Example 
  ```
  $ computeMatrix reference-point --referencePoint center -bs 50 -a 500 -b 500 -p 4 -S 1000_mapped.combined.bw --regionsFileName 1000_mapped_updated.bed --outFileName matrix.MAT
  ```
This example calculates the average methylation signal in 50 bp bins from 500 bp upstream to 500 bp downstream of each region center in the BED file. The result is saved to matrix.mat, ready for heatmap visualization in Step 6.

### Step 6: Visualize Methylation with a [Heatmap](https://github.com/KeleCant/Arabidopsis-6mA-Detection-Pipeline/blob/main/Figure%203.pdf)
To visualize the methylation signal across regions of interest, we use the plotHeatmap tool from the deepTools suite. This command generates a publication-quality heatmap based on the matrix file (.mat) produced in the previous step (typically via computeMatrix). The command allows you to customize the color scheme for the heatmap and output the result in different formats, such as PNG, SVG, or PDF.

  ```
  $ plotHeatmap -m <matrix_file> -o <output_image> --colorList <low_color,high_color>
  ```
- -m <matrix_file>: Path to the matrix file generated by computeMatrix.

- -o <output_image>: Desired output file name and format (e.g., .png, .svg, .pdf).

- --colorList <low_color,high_color>: Defines the gradient used in the heatmap, from low signal (first color) to high signal (second color). Colors should be specified as named colors or hex codes.

Example:
  ```
  $ plotHeatmap -m matirix.MAT -o heatmap.png --colorList white,darkred
  ```
This command will generate a heatmap image (heatmap.png) with white representing the lowest methylation signal and dark red representing the highest.

### Step 7: Visualize Data in [Integrative Genomics Viewer (IGV)](https://github.com/KeleCant/Arabidopsis-6mA-Detection-Pipeline/blob/main/Figure%201.pdf)
The final step involves visualizing your aligned DNA/RNA reads and methylation signal data in Integrative Genomics Viewer (IGV), a desktop tool for interactive exploration of genomic data. IGV enables high-resolution inspection of genomic features, methylation levels, and expression patterns at specific loci.

**Step-by-Step Instructions**
1. Download and install [IGV](https://igv.org/download/html/oldtempfixForDownload.html)
2. Launch IGV
  - Open IGV and select A. thaliana (TAIR10) as the reference genome from the genome dropdown menu. (This loads the RefSeq Genes track automatically.)
3. Prepare Your Files
  Ensure the following files are located in the same directory:
    - Aligned DNA .bam file and corresponding .bam.bai index file (from pbmm2)
    - Aligned RNA .bam file and corresponding .bam.bai index file
    - Methylation BigWig .bw files (from Step 4)
4. Load the BAM Files
  - Use File > Load from File to open both the DNA and RNA .bam files.
  - IGV will automatically generate two tracks per file:
    - Coverage track (summarized read depth)
    - Reads track (individual alignments)
  - You will now see 4 tracks: DNA coverage, DNA reads, RNA coverage, and RNA reads.
5. Load the BigWig File
  - Load the .bw file using File > Load from File.
  - This will add a methylation signal track, displaying smoothed methylation levels across the genome.
6. Navigate to a Region of Interest
  - In the search bar at the top of IGV, enter the genomic coordinates of the region you'd like to view. Example: Chr5:8647136-8651646 (used in [Figure 1](https://github.com/KeleCant/Arabidopsis-6mA-Detection-Pipeline/blob/main/Figure%201.pdf))
7. Refine Your View
  - Right-click the DNA reads track and select "Remove Track".
  - Repeat this for the RNA reads track.
  - This leaves you with the following four key tracks:
      - DNA coverage
      - RNA coverage
      - BigWig methylation signal
      - RefSeq Genes (reference annotation)

Final Track Layout (for visualization)
  - RefSeq Genes – gene model annotation
  - DNA Coverage – overall depth of DNA reads
  - RNA Coverage – overall depth of RNA reads
  - Methylation Signal (BigWig) – 6mA signal intensity
