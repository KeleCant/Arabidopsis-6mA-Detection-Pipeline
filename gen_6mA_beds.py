import argparse
import os

# Chromosome size limits
CHROM_SIZES = {
    "chr1": 30427671,
    "chr2": 19698289,
    "chr3": 23459830,
    "chr4": 18585056,
    "chr5": 26975502,
    "chrm": 367808,
    "chrc": 154478
}

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

def extract_6ma_to_bed(input_file, output_prefix):
    """Extracts 6mA (A+a) modifications and writes them to strand-specific BED files using proper genomic positions."""
    temp_pos_bed = output_prefix + "_pos.temp.bed"
    temp_neg_bed = output_prefix + "_neg.temp.bed"

    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(temp_pos_bed, 'w', encoding='utf-8') as pos_bed, \
         open(temp_neg_bed, 'w', encoding='utf-8') as neg_bed:

        for line in infile:
            if line.startswith('@'):
                continue  # Skip headers

            parts = line.rstrip('\n').split('\t')
            if len(parts) < 13:
                continue

            chrom = parts[2]
            try:
                flag = int(parts[1])
                chrom_start = int(parts[3]) - 1  # 0-based
            except ValueError:
                continue

            strand = '-' if flag & 16 else '+'
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

                            # Absolute position from chrom_start
                            start = chrom_start + rel_pos if strand == '+' else chrom_start - rel_pos
                            end = start + 1

                            if chrom in CHROM_SIZES and 0 <= start < CHROM_SIZES[chrom]:
                                bed_line = f"{chrom}\t{start}\t{end}\t{score:.4f}\n"
                                if strand == '+':
                                    pos_bed.write(bed_line)
                                else:
                                    neg_bed.write(bed_line)

                            ml_index += 1
                    else:
                        skip_count = len(mm[3:].split(','))
                        ml_index += skip_count

    pos_final = output_prefix + "_pos.bed"
    neg_final = output_prefix + "_neg.bed"

    sort_bed_file(temp_pos_bed, pos_final)
    sort_bed_file(temp_neg_bed, neg_final)

    merge_sorted_bed_records(pos_final)
    merge_sorted_bed_records(neg_final)

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

    if prev_chrom is not None:
        merged.append(f"{prev_chrom}\t{prev_start}\t{prev_end}\t{total_score:.4f}\n")

    with open(bed_file, 'w', encoding='utf-8') as outfile:
        outfile.writelines(merged)

def main():
    parser = argparse.ArgumentParser(description="Extract 6mA (A+a) modifications to strand-specific BED files.")
    parser.add_argument("input_file", help="Input SAM file")
    args = parser.parse_args()
    output_prefix = args.input_file.replace(".sam", "_6mA")
    extract_6ma_to_bed(args.input_file, output_prefix)
    print(f"6mA extraction complete!\n → {output_prefix}_pos.bed\n → {output_prefix}_neg.bed")

if __name__ == "__main__":
    main()
