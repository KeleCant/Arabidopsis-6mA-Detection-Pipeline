#!/usr/bin/env nextflow

process heatmap {
    input:
    path matrix

    output:
    path "${matrix.baseName}_heatmap.png"

    script:
    def heatmap_name = matrix.baseName + "_heatmap.png"
    """
    plotHeatmap -m $matrix \
        -o ${heatmap_name} \
        --colorList ${params.lowColour},${params.highColour}
    """
}
