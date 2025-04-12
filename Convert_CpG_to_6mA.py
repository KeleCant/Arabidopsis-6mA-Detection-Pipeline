def process_large_file(input_file, output_file):
    """Processes SAM file, removing 'C+m' markers and replacing 'A+a' markers with 'C+m' in MM and ML tags, keeping them aligned."""
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if line.startswith('@'):
                outfile.write(line)
                continue

            parts = line.rstrip('\n').split('\t')

            # Ensure there are enough parts to modify
            if len(parts) > 12:
                # Modify MM and ML tags (parts[12] and parts[11])
                mm_field = parts[12]
                ml_field = parts[11]
                
                if mm_field.startswith('MM:Z:') and ml_field.startswith('ML:B:C,'):
                    mm_values = mm_field[5:].strip(';').split(';')  # MM:Z: field values
                    ml_values = ml_field[7:].split(',')  # ML:B:C, values (fix by not removing leading comma)

                    # Temporary lists to store the modified MM and ML values
                    modified_mm_values = []
                    modified_ml_values = []

                    # Iterate through MM and ML values and make changes
                    mm_index = 0  # Counter for MM values
                    for mm_value in mm_values:
                        # Count how many numbers are in this modification type
                        mm_numbers = mm_value.split(',')
                        num_numbers = len(mm_numbers)
                        
                        if mm_value.startswith('C+m'):
                            # Skip the corresponding ML numbers if it is a C+m modification
                            mm_index += num_numbers  # Skip this many numbers in ML as well
                            continue  # Remove this entry from both MM and ML (C+m marker)
                        
                        if mm_value.startswith('A+a'):
                            mm_value = 'C+m' + mm_value[3:]  # Replace A+a with C+m in MM
                        
                        # Add the modified MM and corresponding ML values
                        modified_mm_values.append(mm_value)
                        modified_ml_values.extend(ml_values[mm_index:mm_index + num_numbers])
                        mm_index += num_numbers  # Move the index forward by the number of numbers in this modification

                    # Update the MM:Z: and ML:B:C, tags with the modified values
                    parts[12] = 'MM:Z:' + ';'.join(modified_mm_values) + ';'
                    parts[11] = 'ML:B:C,' + ','.join(modified_ml_values)

            # Reconstruct the line, ensuring no empty fields are included
            new_parts = [field for field in parts if field]
            outfile.write('\t'.join(new_parts) + '\n')

def main():
    parser = argparse.ArgumentParser(description="Modify SAM file MM and ML tags.")
    parser.add_argument("input_file", help="Path to the input SAM file")
    args = parser.parse_args()
    output_file = args.input_file.replace(".sam", "_modified.sam")
    process_large_file(args.input_file, output_file)
    print(f"Processing complete! Output saved to: {output_file}")

if __name__ == "__main__":
    main()
