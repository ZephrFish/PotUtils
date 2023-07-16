import sys
import re
import binascii

regex = re.compile(r"\$HEX\[(.*?)\]")

if len(sys.argv) < 3:
    print("Usage: python Hex2WordList.py <potfile> <output>")
    sys.exit(1)

potfile_path = sys.argv[1]
output_path = sys.argv[2]

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
