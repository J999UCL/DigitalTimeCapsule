import subprocess
import time
import shutil
import os
import sys

def run_with_t(image_path, t):
    image_copy_path = f"{os.path.splitext(image_path)[0]}_copy_{t}{os.path.splitext(image_path)[1]}"
    shutil.copy(image_path, image_copy_path)

    process = subprocess.Popen([sys.executable, 'run.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True)
    process.stdin.write(f"{image_copy_path}\n{t}\n")
    process.stdin.flush()

    output_lines = []
    elapsed_time = None
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            output_lines.append(output)
            if "Decryption complete: " in output:
                elapsed_time = float(output.split("Decryption complete: ")[1].strip())

    return t, elapsed_time, output_lines

def main():
    image_path = "decrypted_image.png"
    ts = range(1, 100)
    results = []

    for t in ts:
        print(t)
        t, elapsed_time, output_lines = run_with_t(image_path, t)
        print(t)
        print(elapsed_time)
        if elapsed_time is not None:
            results.append((t, elapsed_time))
            print(f"t = {t}, Time taken = {elapsed_time:.6f} seconds")
        else:
            print(f"t = {t}, Decryption failed")
            print("Output:\n", "".join(output_lines))

    # Save results to a file
    with open('timing_results.txt', 'w') as f:
        f.write("t, Time taken (seconds)\n")
        for t, elapsed_time in results:
            f.write(f"{t}, {elapsed_time:.6f}\n")

if __name__ == "__main__":
    main()