#!/usr/bin/env nextflow

process cpgtools {
    publishDir 'cpgaligned', mode: 'copy'

    conda "./env.yml" // Specify your Conda environment file

    input:
    //path aligned_bam_name
    tuple(path(bam_file), path(bai_file))    

    output:
    tuple val(bam_file.baseName), path("${bam_file.baseName}*.bigwig"), path("${bam_file.baseName}*.bed")

    script:
    def output_prefix = bam_file.baseName
    """
    aligned_bam_to_cpg_scores --bam ${bam_file} --output-prefix ${output_prefix}
    """
}

workflow cpgtoolswork {
    take:
    aligned_bam_name

    main:
    result = run_cpgtools(aligned_bam_name)

    emit:
    result
}
