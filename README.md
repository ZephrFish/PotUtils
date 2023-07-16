# PotFileUtils
This repo contains various utilities for manipulating the potfile in hashcat, the first two are for mapping the $HEX[] values to actual words and the second will parse your potfile and output to a wordlist. 

Inspired by a few utils that [John Carroll](https://twitter.com/TheContractorio) wrote in go initially.

## Modes
1. pot2words - Reads an input file where each line is separated by ":", and writes the last field of each line to the output file.

2. hex2words - Reads a potfile where hexadecimal strings are found in the second field of each line, separates by ":", decodes the hexadecimal strings into plain text, and writes the decoded strings to the output file.

3. both - Runs both the pot2words and hex2words modes and writes the combined output to the output file. This mode also removes duplicates from the output.

## Usage
```
python PotUtils.py--mode [MODE] --input [Potfile or path to potfile] --output [OUTPUT_FILE_PATH]
```

## Example
```
python PotUtils.py --mode pot2words --input input.txt --output output.txt
python PotUtils.py --mode hex2words --input potfile.txt --output output.txt
python PotUtils.py --mode both --input input.txt --output output.txt
```

## Future Plans
Thread both scripts to allow for bigger potfiles
