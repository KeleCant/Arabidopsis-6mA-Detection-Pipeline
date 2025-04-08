#!/usr/bin/env nextflow

process matrix {
    input:
    path bigwigs
    path bedfile
    
    output:
    path "matrix.mat"
    
    script:
    """
    computeMatrix reference-point --referencePoint center \
        -bs ${params.binSize} -a ${params.BP_after_BED} -b ${params.BP_before_BED} -p 4 \
        -S $bigwigs \
        --regionsFileName $bedfile \
        --outFileName matrix.mat
    """
}
