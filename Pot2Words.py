import sys

if len(sys.argv) < 3:
    print("Usage: python Pot2Words.py <potfile> <output_file_path>")
    sys.exit(1)

input_file_path = sys.argv[1]
output_file_path = sys.argv[2]

with open(input_file_path, "r") as input_file, open(output_file_path, "w") as output_file:
    for line in input_file:
        fields = line.strip().split(":")
        last_field = fields[-1]
        output_file.write(last_field + "\n")
