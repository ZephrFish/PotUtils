import sys
import re
import binascii
import argparse
import tempfile
import os

def pot2words(input_file_path, output_file_path):
    with open(input_file_path, "r") as input_file, open(output_file_path, "w") as output_file:
        for line in input_file:
            fields = line.strip().split(":")
            last_field = fields[-1]
            output_file.write(last_field + "\n")
    print("Conversion complete. Check", output_file_path)

def hex2words(potfile_path, output_path):
    regex = re.compile(r"\$HEX\[(.*?)\]")

    try:
        with open(potfile_path, "r") as file:
            lines = file.readlines()
    except IOError as e:
        print(f"Error opening potfile: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        outfile = open(output_path, "w", encoding="utf-8")
    except IOError as e:
        print(f"Error opening output file: {e}", file=sys.stderr)
        sys.exit(1)

    for line in lines:
        fields = line.split(":")
        if len(fields) > 1:
            matches = regex.findall(fields[1])
            if len(matches) > 0:
                hex_string = matches[0]
                try:
                    text = binascii.unhexlify(hex_string)
                    decoded_text = text.decode("utf-8", errors="replace")
                    outfile.write(decoded_text + "\n")
                except binascii.Error as e:
                    print(f"Error decoding hex string: {e}", file=sys.stderr)

    outfile.close()
    print("Conversion complete. Check", output_path)

def merge_unique(input_file1, input_file2, output_file):
    words = set()

    with open(input_file1, "r") as file1, open(input_file2, "r") as file2:
        words.update(line.strip() for line in file1)
        words.update(line.strip() for line in file2)

    with open(output_file, "w") as out_file:
        for word in words:
            out_file.write(word + "\n")

    print("Merged and unique output complete. Check", output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI tool for data conversion.")
    parser.add_argument("--mode", choices=["pot2words", "hex2words", "both"], required=True, help="Conversion mode to use.")
    parser.add_argument("--input", required=True, help="Path to the input file.")
    parser.add_argument("--output", required=True, help="Path to the output file.")
    args = parser.parse_args()

    if args.mode == "pot2words":
        pot2words(args.input, args.output)
    elif args.mode == "hex2words":
        hex2words(args.input, args.output)
    elif args.mode == "both":
        with tempfile.NamedTemporaryFile(delete=False) as tmp1, tempfile.NamedTemporaryFile(delete=False) as tmp2:
            pot2words(args.input, tmp1.name)
            hex2words(args.input, tmp2.name)
            merge_unique(tmp1.name, tmp2.name, args.output)
            os.unlink(tmp1.name)
            os.unlink(tmp2.name)
