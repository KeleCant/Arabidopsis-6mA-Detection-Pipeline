# First version

import argparse
import os

def decode_mm_deltas(deltas):
    """Convert MM delta string with dots into absolute positions."""
    positions = []
    last_pos = 0
    last_delta = 0
    for d in deltas:
        if d == '.':
            delta = last_delta
        else:
            delta = int(d)
            last_delta = delta
        last_pos += delta
        positions.append(last_pos)
    return positions

def extract_6ma_to_bed(input_file, output_bed):
    """Extracts 6mA (A+a) modifications and writes them to a BED file."""
    temp_bedfile = output_bed + ".temp"
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(temp_bedfile, 'w', encoding='utf-8') as bedfile:

        for line in infile:
            if line.startswith('@'):
                continue  # Skip headers

            parts = line.rstrip('\n').split('\t')
            if len(parts) < 13:
                continue

            chrom = parts[2]
            try:
                chrom_start = int(parts[3]) - 1  # 0-based
            except ValueError:
                continue

            mm_field = next((f for f in parts if f.startswith('MM:Z:')), None)
            ml_field = next((f for f in parts if f.startswith('ML:B:C,')), None)

            if mm_field and ml_field:
                mm_values = mm_field[5:].strip(';').split(';')
                ml_values = list(map(int, ml_field[7:].split(',')))

                ml_index = 0
                for mm in mm_values:
                    if mm.startswith('A+a'):
                        raw_deltas = mm[3:].split(',')
                        try:
                            positions = decode_mm_deltas(raw_deltas)
                        except ValueError:
                            continue

                        for rel_pos in positions:
                            if ml_index >= len(ml_values):
                                break
                            score = (ml_values[ml_index] + 1) / 256
                            start = chrom_start + rel_pos
                            end = start + 1
                            bedfile.write(f"{chrom}\t{start}\t{end}\t{score:.4f}\n")
                            ml_index += 1
                    else:
                        skip_count = len(mm[3:].split(','))
                        ml_index += skip_count

    sort_bed_file(temp_bedfile, output_bed)
    merge_sorted_bed_records(output_bed)

def sort_bed_file(input_bed, output_bed):
    """Sorts a BED file by chromosome and start position."""
    with open(input_bed, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    lines.sort(key=lambda line: (line.split('\t')[0], int(line.split('\t')[1])))

    with open(output_bed, 'w', encoding='utf-8') as outfile:
        outfile.writelines(lines)

    os.remove(input_bed)

def merge_sorted_bed_records(bed_file):
    """Merge records at the same chrom/start/end and sum their scores."""
    with open(bed_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    merged = []
    prev_chrom, prev_start, prev_end, total_score = None, None, None, 0.0

    for line in lines:
        chrom, start, end, score = line.strip().split('\t')
        start, end = int(start), int(end)
        score = float(score)

        if (chrom == prev_chrom) and (start == prev_start) and (end == prev_end):
            total_score += score
        else:
            if prev_chrom is not None:
                merged.append(f"{prev_chrom}\t{prev_start}\t{prev_end}\t{total_score:.4f}\n")
            prev_chrom, prev_start, prev_end, total_score = chrom, start, end, score

    # Add the last record
    if prev_chrom is not None:
        merged.append(f"{prev_chrom}\t{prev_start}\t{prev_end}\t{total_score:.4f}\n")

    with open(bed_file, 'w', encoding='utf-8') as outfile:
        outfile.writelines(merged)

def main():
    parser = argparse.ArgumentParser(description="Extract 6mA (A+a) modifications to BED.")
    parser.add_argument("input_file", help="Input SAM file")
    args = parser.parse_args()
    output_bed = args.input_file.replace(".sam", "_6mA.bed")
    extract_6ma_to_bed(args.input_file, output_bed)
    print(f"6mA extraction complete! BED file saved to: {output_bed}")

if __name__ == "__main__":
    main()
