package main

import (
	"bufio"
	"encoding/hex"
	"flag"
	"fmt"
	"os"
	"regexp"
	"strings"
	"sync"
)

func potWorker(workerID int, jobs <-chan string, wg *sync.WaitGroup, outputPath string) {
	defer wg.Done()
	outputFile, err := os.Create(fmt.Sprintf("%s_%d", outputPath, workerID))
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error creating output file: %v\n", err)
		return
	}
	defer outputFile.Close()
	writer := bufio.NewWriter(outputFile)
	defer writer.Flush()

	for line := range jobs {
		fields := strings.Split(line, ":")
		if len(fields) > 0 {
			lastField := fields[len(fields)-1]
			writer.WriteString(lastField + "\n")
		}
	}
	fmt.Printf("Worker %d completed.\n", workerID)
}

func pot2wordsThreaded(inputFilePath, outputFilePath string, numThreads int) {
	jobs := make(chan string, numThreads)
	var wg sync.WaitGroup

	for i := 0; i < numThreads; i++ {
		wg.Add(1)
		go potWorker(i, jobs, &wg, outputFilePath)
	}

	inputFile, err := os.Open(inputFilePath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error opening input file: %v\n", err)
		os.Exit(1)
	}
	defer inputFile.Close()

	scanner := bufio.NewScanner(inputFile)
	for scanner.Scan() {
		jobs <- scanner.Text()
	}
	close(jobs)
	wg.Wait()

	fmt.Println("All workers completed.")
	mergeFiles(outputFilePath, numThreads)
	fmt.Println("Conversion complete. Check", outputFilePath)
}

func hexWorker(workerID int, jobs <-chan string, wg *sync.WaitGroup, outputPath string) {
	defer wg.Done()
	outputFile, err := os.Create(fmt.Sprintf("%s_%d", outputPath, workerID))
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error creating output file: %v\n", err)
		return
	}
	defer outputFile.Close()
	writer := bufio.NewWriter(outputFile)
	defer writer.Flush()

	regex := regexp.MustCompile(`\$HEX\[(.*?)\]`)

	for line := range jobs {
		fields := strings.Split(line, ":")
		if len(fields) > 1 {
			matches := regex.FindAllStringSubmatch(fields[1], -1)
			for _, match := range matches {
				if len(match) > 1 {
					hexString := match[1]
					decodedText, err := hex.DecodeString(hexString)
					if err != nil {
						fmt.Fprintf(os.Stderr, "Error decoding hex string: %v\n", err)
						continue
					}
					writer.WriteString(string(decodedText) + "\n")
				}
			}
		}
	}
	fmt.Printf("Worker %d completed.\n", workerID)
}

func hex2wordsThreaded(inputFilePath, outputFilePath string, numThreads int) {
	jobs := make(chan string, numThreads)
	var wg sync.WaitGroup

	for i := 0; i < numThreads; i++ {
		wg.Add(1)
		go hexWorker(i, jobs, &wg, outputFilePath)
	}

	inputFile, err := os.Open(inputFilePath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error opening input file: %v\n", err)
		os.Exit(1)
	}
	defer inputFile.Close()

	scanner := bufio.NewScanner(inputFile)
	for scanner.Scan() {
		jobs <- scanner.Text()
	}
	close(jobs)
	wg.Wait()

	fmt.Println("All workers completed.")
	mergeFiles(outputFilePath, numThreads)
	fmt.Println("Conversion complete. Check", outputFilePath)
}

func mergeFiles(outputFilePath string, numThreads int) {
	outputFile, err := os.Create(outputFilePath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error creating final output file: %v\n", err)
		return
	}
	defer outputFile.Close()
	writer := bufio.NewWriter(outputFile)
	defer writer.Flush()

	for i := 0; i < numThreads; i++ {
		workerFile, err := os.Open(fmt.Sprintf("%s_%d", outputFilePath, i))
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error opening worker output file: %v\n", err)
			continue
		}
		scanner := bufio.NewScanner(workerFile)
		for scanner.Scan() {
			writer.WriteString(scanner.Text() + "\n")
		}
		workerFile.Close()
		os.Remove(fmt.Sprintf("%s_%d", outputFilePath, i))
	}
}

func mergeUnique(inputFile1, inputFile2, outputFile string) {
	words := make(map[string]struct{})
	readFile := func(path string) {
		file, err := os.Open(path)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error opening input file: %v\n", err)
			return
		}
		defer file.Close()
		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			words[scanner.Text()] = struct{}{}
		}
	}

	readFile(inputFile1)
	readFile(inputFile2)

	outputFileHandle, err := os.Create(outputFile)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error creating output file: %v\n", err)
		return
	}
	defer outputFileHandle.Close()
	writer := bufio.NewWriter(outputFileHandle)
	defer writer.Flush()

	for word := range words {
		writer.WriteString(word + "\n")
	}

	fmt.Println("Merged and unique output complete. Check", outputFile)
}

func main() {
	mode := flag.String("mode", "", "Conversion mode to use (pot2words, hex2words, both)")
	modeShort := flag.String("m", "", "Conversion mode to use (pot2words, hex2words, both)")

	inputPath := flag.String("input", "", "Path to the input file")
	inputPathShort := flag.String("i", "", "Path to the input file")

	outputPath := flag.String("output", "", "Path to the output file")
	outputPathShort := flag.String("o", "", "Path to the output file")

	numThreads := flag.Int("threads", 1, "Number of worker threads to use")
	numThreadsShort := flag.Int("t", 1, "Number of worker threads to use")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage of %s:\n", os.Args[0])
		flag.VisitAll(func(f *flag.Flag) {
			if f.Name == "mode" {
				fmt.Fprintf(os.Stderr, "  -m, -mode string\n\t%s\n", f.Usage)
			} else if f.Name == "input" {
				fmt.Fprintf(os.Stderr, "  -i, -input string\n\t%s\n", f.Usage)
			} else if f.Name == "output" {
				fmt.Fprintf(os.Stderr, "  -o, -output string\n\t%s\n", f.Usage)
			} else if f.Name == "threads" {
				fmt.Fprintf(os.Stderr, "  -t, -threads int\n\t%s\n", f.Usage)
			}
		})
	}

	flag.Parse()

	if (*mode == "" && *modeShort == "") || (*inputPath == "" && *inputPathShort == "") || (*outputPath == "" && *outputPathShort == "") {
		flag.Usage()
		os.Exit(1)
	}

	actualMode := *mode
	if actualMode == "" {
		actualMode = *modeShort
	}

	actualInputPath := *inputPath
	if actualInputPath == "" {
		actualInputPath = *inputPathShort
	}

	actualOutputPath := *outputPath
	if actualOutputPath == "" {
		actualOutputPath = *outputPathShort
	}

	actualNumThreads := *numThreads
	if actualNumThreads == 1 {
		actualNumThreads = *numThreadsShort
	}

	switch actualMode {
	case "pot2words":
		pot2wordsThreaded(actualInputPath, actualOutputPath, actualNumThreads)
	case "hex2words":
		hex2wordsThreaded(actualInputPath, actualOutputPath, actualNumThreads)
	case "both":
		tempFile1 := actualOutputPath + "_temp1"
		tempFile2 := actualOutputPath + "_temp2"
		pot2wordsThreaded(actualInputPath, tempFile1, actualNumThreads)
		hex2wordsThreaded(actualInputPath, tempFile2, actualNumThreads)
		mergeUnique(tempFile1, tempFile2, actualOutputPath)
		os.Remove(tempFile1)
		os.Remove(tempFile2)
	default:
		fmt.Println("Invalid mode. Use 'pot2words', 'hex2words', or 'both'")
	}
}
