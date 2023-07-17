import sys
import re
import binascii
import argparse
import tempfile
import os
import queue
import threading


def pot_worker(worker_id, queue, output_path):
    with open(f"{output_path}_{worker_id}", "w") as output_file:
        while True:
            line = queue.get()
            if line is None:  # sentinel value indicating all items have been processed
                break
            fields = line.strip().split(":")
            last_field = fields[-1]
            output_file.write(last_field + "\n")
    print(f"Worker {worker_id} completed.")

def pot2words_threaded(input_file_path, output_file_path, num_threads):
    lines_queue = queue.Queue()

    # create and start worker threads
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=pot_worker, args=(i, lines_queue, output_file_path))
        t.start()
        threads.append(t)

    # read the input file and enqueue lines for the workers to process
    try:
        with open(input_file_path, "r", errors='replace') as input_file:
            for line in input_file:
                lines_queue.put(line.strip())
    except IOError as e:
        print(f"Error opening input file: {e}", file=sys.stderr)
        sys.exit(1)

    # enqueue sentinel values to let workers know when all items have been processed
    for i in range(num_threads):
        lines_queue.put(None)

    # wait for all workers to finish
    for t in threads:
        t.join()

    print("All workers completed.")

    # merge output files from workers into final output file
    with open(output_file_path, "w") as outfile:
        for i in range(num_threads):
            with open(f"{output_file_path}_{i}", "r") as worker_outfile:
                for line in worker_outfile:
                    outfile.write(line)
    # delete worker output files
    for i in range(num_threads):
        os.remove(f"{output_file_path}_{i}")

    print("Conversion complete. Check", output_file_path)


def hex_worker(worker_id, queue, output_path):
    regex = re.compile(r"\$HEX\[(.*?)\]")

    with open(f"{output_path}_{worker_id}", "w", encoding="utf-8") as outfile:
        while True:
            line = queue.get()
            if line is None:  # sentinel value indicating all items have been processed
                break
            fields = line.split(":")
            if len(fields) > 1:
                matches = regex.findall(fields[1])
                if len(matches) > 0:
                    hex_string = matches[0]
                    try:
                        text = binascii.unhexlify(hex_string)
                        decoded_text = text.decode("cp1253", errors="replace")
                        outfile.write(decoded_text + "\n")
                    except binascii.Error as e:
                        print(f"Error decoding hex string: {e}", file=sys.stderr)
    print(f"Worker {worker_id} completed.")

def hex2words_threaded(input_file_path, output_file_path, num_threads):
    lines_queue = queue.Queue()

    # create and start worker threads
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=hex_worker, args=(i, lines_queue, output_file_path))
        t.start()
        threads.append(t)

    # read the input file and enqueue lines for the workers to process
    try:
        with open(input_file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                lines_queue.put(line.strip())
    except IOError as e:
        print(f"Error opening potfile: {e}", file=sys.stderr)
        sys.exit(1)

    # enqueue sentinel values to let workers know when all items have been processed
    for i in range(num_threads):
        lines_queue.put(None)

    # wait for all workers to finish
    for t in threads:
        t.join()

    print("All workers completed.")

    # merge output files from workers into final output file
    with open(output_file_path, "w", encoding="utf-8") as outfile:
        for i in range(num_threads):
            with open(f"{output_file_path}_{i}", "r", encoding="utf-8") as worker_outfile:
                for line in worker_outfile:
                    outfile.write(line)
    # delete worker output files
    for i in range(num_threads):
        os.remove(f"{output_file_path}_{i}")

    print("Conversion complete. Check", output_file_path)


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
    parser.add_argument("--threads", type=int, default=1, help="Number of worker threads to use.")
    args = parser.parse_args()

    if args.mode == "pot2words":
        pot2words_threaded(args.input, args.output, args.threads)
    elif args.mode == "hex2words":
        hex2words_threaded(args.input, args.output, args.threads)
    elif args.mode == "both":
        with tempfile.NamedTemporaryFile(delete=False) as tmp1, tempfile.NamedTemporaryFile(delete=False) as tmp2:
            pot2words_threaded(args.input, tmp1.name, args.threads)
            hex2words_threaded(args.input, tmp2.name, args.threads)
            merge_unique(tmp1.name, tmp2.name, args.output)
            os.unlink(tmp1.name)
            os.unlink(tmp2.name)

