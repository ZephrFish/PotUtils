# GoPotUtils

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
