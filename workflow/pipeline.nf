#!/usr/bin/env nextflow

nextflow.enable.dsl=2

include { pbmm2 } from './pbmm2.nf'
include { cpgtools } from './cpgtools.nf'
include { matrix } from './matrix.nf'
include { heatmap } from './heatmap.nf'


workflow {
    bam_file = file(params.BAMFILEOFINTEREST)
    genome_file = file(params.GENOMEFILEOFINTEREST)

    //aligned_bam = pbmm2(genome_file, bam_file)

    //all_outputs = pbmm2(genome_file, bam_file)

    //all_outputs
    //.filter { it[0].name.endsWith('.bam') } // assuming BAM is first in the tuple
    //.map { it[0] } // extract just the BAM file
    //.set { aligned_bam }

    all_outputs = pbmm2(genome_file, bam_file)

    all_outputs
      .filter { it[0].name.endsWith('.bam') } // Filter the BAM files from the output
      .map { bam_tuple -> // bam_tuple is now the input tuple
          tuple(bam_tuple[0], bam_tuple[1]) // Access bam_tuple[1] as BAI
      }
      .set { aligned_bam }

    cpg_out = cpgtools(aligned_bam)
    cpgtools_output_bigwig = cpg_out.map { id, bigwig, bed -> bigwig }
    cpgtools_output_bed = cpg_out.map { id, bigwig, bed -> bed }  

    matrix_out = matrix(cpgtools_output_bigwig, cpgtools_output_bed)

    heatmap(matrix_out)  
}
