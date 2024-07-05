# PotFileUtils

This repo contains various utilities for manipulating the potfile in hashcat. The first two are for mapping the $HEX[] values to actual words. The second will parse your potfile and output to a wordlist.

Inspired by a few utils that [John Carroll](https://twitter.com/TheContractorio) initially wrote in Go. I have since rewritten it in Go to accomodate cross-platform execution, the example is in exe but can be compiled for Linux and MacOS too.

## Modes

1. **pot2words** - Reads an input file where each line is separated by ":", and writes the last field of each line to the output file.

2. **hex2words** - Reads a potfile where hexadecimal strings are found in the second field of each line, separated by ":", decodes the hexadecimal strings into plain text, and writes the decoded strings to the output file.

3. **both** - Runs the pot2words and hex2words modes and writes the combined output to the output file. This mode also removes duplicates from the output.

## Flavours

- Python
- Go

### Go Build Notes

To build the GoPotUtils project, follow the steps below.

#### Prerequisites

- Ensure you have [Go](https://golang.org/dl/) installed on your system.
- Open a terminal or PowerShell.

1. **Navigate to the project directory**:
   ```sh
   cd /path/to/GoPotUtils
   ```

2. **Build the Go binary**:
   ```PowerShell
   & 'c:\Program Files\Go\bin\go.exe' build -ldflags="-s -w" -gcflags="all=-trimpath=C:\Path\To\Tools\PotUtils\GoPotUtils" -asmflags="all=-trimpath=C:\Path\To\Tools\PotUtils\GoPotUtils" -o GoPotUtils.exe .\GoPotUtils.go
   ```

### Go Usage

There are two options for executing this either with long form or short form flags:

```
  -i, -input string
        Path to the input file
  -m, -mode string
        Conversion mode to use (pot2words, hex2words, both)
  -o, -output string
        Path to the output file
  -t, -threads int
        Number of worker threads to use
```

Go Example usage:

```PowerShell
.\GoPotUtils.exe --mode pot2words --input input.txt --output output.txt --threads 10
.\GoPotUtils.exe --mode hex2words --input potfile.txt --output output.txt --threads 10
.\GoPotUtils.exe --mode both --input input.txt --output output.txt --threads 10
.\GoPotUtils.exe -m pot2words -i input.txt -o output.txt -t 10
.\GoPotUtils.exe -m hex2words -i potfile.txt -o output.txt -t 10
.\GoPotUtils.exe -m both -i input.txt -o output.txt -t 10
```

### Python Usage

```
python PotUtils.py --mode [MODE] --input [Potfile or path to potfile] --output [OUTPUT_FILE_PATH] --threads <number of threads>
```

Tested on a 27GB Potfile, and while it takes a wee bit of time with threading, it runs!

![27G Potfile](image.png)

#### Example

```
python PotUtils.py --mode pot2words --input input.txt --output output.txt --threads 10
python PotUtils.py --mode hex2words --input potfile.txt --output output.txt --threads 10
python PotUtils.py --mode both --input input.txt --output output.txt --threads 10
```

When it uses threads in either pot2words or hex2words, the script will create X number of temporary files i.e. 1 per thread, then merge them at the end. When using both mode, it'll do the same but merge all the outputs into one file.
