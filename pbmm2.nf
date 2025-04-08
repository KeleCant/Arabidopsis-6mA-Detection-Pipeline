#!/usr/bin/env nextflow

process pbmm2 {
    publishDir 'aligned', mode: 'copy'

    input:
    path genome_file
    path bam_file
    
    output:
    path "*.bam*"  // Capturing the output BAM file
    //tuple val(aligned_bam.baseName), path("${aligned_bam.baseName}.bam"), path("${aligned_bam.baseName}.bam.bai")


    script:
    def output_bam = bam_file.baseName + "_aligned.bam"
    """
    pbmm2 align ${genome_file} ${bam_file} ${output_bam} --sort --preset CCS
    """
}
