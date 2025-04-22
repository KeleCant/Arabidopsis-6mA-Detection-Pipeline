#!/usr/bin/env nextflow

nextflow.enable.dsl=2

process matrix {
    input:
    path bigwigs
    path bedfile
    
    output:
    path "matrix.mat"
    
    script:
    """
    bed_unzipped=\$(basename "$bedfile" .gz)
    gunzip -c $bedfile > \$bed_unzipped

    computeMatrix reference-point --referencePoint center \
        -bs ${params.binSize} -a ${params.BP_after_BED} -b ${params.BP_before_BED} -p 4 \
        -S $bigwigs \
        --regionsFileName "\$bed_unzipped" \
        --outFileName matrix.mat
    """
}
