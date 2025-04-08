import sys

def read_bed(file_path):
    """Reads a BED file and returns a list of parsed entries."""
    bed_data = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith("#") or not line.strip():
                    continue  # Skip comments and empty lines

                fields = line.strip().split("\t")
                if len(fields) < 3:
                    print(f"Skipping malformed line: {line.strip()}")
                    continue

                chrom, start, end = fields[:3]
                score = fields[3]
                name = f"{chrom}:{start}-{end}"

                try:
                    start, end, score = int(start), int(end), float(score)  # Convert to integers
                    bed_data.append((chrom, start, end, name, score, "."))  # Store remaining fields if any
                except ValueError:
                    print(f"Skipping invalid coordinate line: {line.strip()}")

        return bed_data

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

def write_bed(file_path, entries):
    with open(file_path, "w") as file:
        for item in entries:
            line = "\t".join(map(str, item)) + "\n"
            file.write(line)

# Example usage
if __name__ == "__main__":
    bed_entries = []
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Error: Provide name of input and output file in the following order")
        print("python convert.py \'path to input file\' \'path to output file\'")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        bed_entries = read_bed(input_file)
        write_bed(output_file, bed_entries)
