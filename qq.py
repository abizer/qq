#!/usr/bin/env python3

import argparse
import os
import sys
import tempfile
import subprocess
from functools import partial
from typing import Callable

# Check for required API keys
NEEDED_KEYS = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")
missing_keys = [key for key in NEEDED_KEYS if not os.getenv(key)]
if missing_keys:
    print(
        f"Error: The following API key(s) are not set: {', '.join(missing_keys)}",
        file=sys.stderr,
    )
    sys.exit(1)


def explain(llm: Callable, query: str) -> None:
    messages = [
        {
            "role": "system",
            "content": r"""
You are an expert in explaining command-line operations across various operating systems and shells. Your task is to provide clear, concise, and accurate explanations of commands, pipelines, and scripts. Follow these guidelines:

1. Break down the command into its constituent parts.
2. Explain each part on a new line, prefixed with the command part itself.
3. For each part, describe its function, any options or flags used, and their effects.
4. If applicable, mention any potential side effects or important considerations.
5. Conclude with a one-line summary of the overall operation.
6. Use technical terminology where appropriate, but ensure explanations are accessible to users with varying levels of expertise.

Examples:

Input: find . -type f -name "*.txt" -exec sed -i 's/foo/bar/g' {} +
Output:
find . - Start searching from the current directory
-type f - Look for regular files only
-name "*.txt" - Match files with names ending in .txt
-exec sed -i 's/foo/bar/g' {} + - For each matched file, execute sed to replace all occurrences of 'foo' with 'bar' in-place
This command finds all .txt files in the current directory and its subdirectories, then replaces all occurrences of 'foo' with 'bar' in each file.

Input: docker run --rm -d --name nginx -p 80:80 -v /host/path:/container/path nginx:latest
Output:
docker run - Run a Docker container
--rm - Automatically remove the container when it exits
-d - Run the container in detached mode (in the background)
--name nginx - Assign the name "nginx" to the container
-p 80:80 - Map port 80 of the host to port 80 in the container
-v /host/path:/container/path - Mount a volume, mapping /host/path on the host to /container/path in the container
nginx:latest - Use the latest version of the nginx image
This command starts a detached nginx container named "nginx", mapping port 80 and a volume, using the latest nginx image.

Input: awk 'BEGIN{FS=OFS=","} NR>1 {sum+=$3; count++} END{print "Average:", sum/count}' data.csv
Output:
awk - Invoke the awk text-processing tool
'BEGIN{FS=OFS=","} - Set the input and output field separator to comma
NR>1 - Skip the first line (assumed to be a header)
{sum+=$3; count++} - For each subsequent line, add the value in the third column to sum and increment count
END{print "Average:", sum/count}' - After processing all lines, print the average
data.csv - The input file to process
This awk command calculates and prints the average of values in the third column of a CSV file, skipping the header row.

Input: grep -r '/opt/home' ~/.*(D.)
Output:
grep - Search for patterns in files
-r - Recursively search subdirectories
'/opt/home' - The pattern to search for
~/.*(D.) - Zsh glob pattern that matches all hidden files and directories in the home directory
This command searches for the string '/opt/home' in all hidden files and directories (dotfiles) in the user's home directory using Zsh-specific globbing.
""",
        },
        {"role": "user", "content": query},
    ]

    for chunk in llm(messages=messages):
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    print()  # Print a newline at the end


def generate(llm: Callable, query: str) -> None:
    messages = [
        {
            "role": "system",
            "content": r"""
You are an expert in generating command-line operations across various operating systems and shells. Your task is to create efficient, effective, and safe commands based on user descriptions. Follow these guidelines:

1. Output only the command or script, with no additional explanation.
2. Ensure the command is correct, efficient, and follows best practices.
3. Use appropriate flags, options, and syntax for the implied operating system or shell.
4. If a specific OS isn't mentioned, default to a POSIX-compliant shell command.
5. Incorporate error handling and safety checks where appropriate.
6. For complex operations, consider using multiple commands connected with pipes or creating a small script.
7. When working with dotfiles or hidden files in Zsh, use the glob pattern ~/.*(D.) to match all hidden files and directories in the home directory.

Examples:

Input: Find all Python files modified in the last 7 days and create a zip archive of them
Output: find . -type f -name "*.py" -mtime -7 -print0 | xargs -0 zip updated_python_files.zip

Input: Monitor system resource usage, logging CPU, memory, and disk usage every 5 seconds to a file named system_usage.log
Output: while true; do echo "$(date): $(top -bn1 | grep load | awk '{printf "CPU Load: %.2f", $(NF-2)}') $(free -m | awk 'NR==2{printf " Memory Usage: %s/%sMB %.2f%%", $3,$2,$3*100/$2 }') $(df -h | awk '$NF=="/"{printf " Disk Usage: %d/%dGB %s", $3,$2,$5}')"; sleep 5; done >> system_usage.log

Input: Create a bash script that backs up all .jpg files in the current directory to a timestamped folder in /backups, compresses the folder, and deletes files older than 30 days
Output: cat << 'EOF' > backup_script.sh
#!/bin/bash
set -e

BACKUP_DIR="/backups/photos_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

find . -maxdepth 1 -type f -name "*.jpg" -exec cp {} "$BACKUP_DIR" \;

tar czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

find /backups -type f -name "photos_*.tar.gz" -mtime +30 -delete

echo "Backup completed successfully"
EOF
chmod +x backup_script.sh

Input: Set up a cron job to run a Python script every day at 3 AM
Output: (crontab -l 2>/dev/null; echo "0 3 * * * /usr/bin/python3 /path/to/your/script.py") | crontab -

Input: Create a Docker command to run a PostgreSQL container with a custom configuration, set a password, and map to a local volume
Output: docker run -d --name postgres_db -e POSTGRES_PASSWORD=mysecretpassword -v /path/to/local/data:/var/lib/postgresql/data -v /path/to/custom/postgresql.conf:/etc/postgresql/postgresql.conf postgres:latest -c 'config_file=/etc/postgresql/postgresql.conf'

Input: Search for all instances of '/opt/home' in my dotfiles using Zsh
Output: grep -r '/opt/home' ~/.*(D.)
""",
        }
    ]

    while True:
        messages.append({"role": "user", "content": query})

        result = ""
        for chunk in llm(messages=messages):
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
                result += content
        print()  # Print a newline at the end

        messages.append({"role": "assistant", "content": result})

        print("exec (x) / edit (e) / reprompt (r): ", end="")
        choice = input().strip().lower()
        match choice:
            case "x":
                os.execlp("zsh", "zsh", "-c", result)
            case "e":
                with tempfile.NamedTemporaryFile(
                    mode="w+", suffix=".txt", delete=False
                ) as tmp:
                    tmp.write(result)
                    tmp_filename = tmp.name

                try:
                    subprocess.run(["vim", tmp_filename], check=True)
                    with open(tmp_filename, "r") as tmp:
                        query = tmp.read().strip()
                finally:
                    os.unlink(tmp_filename)
            case "r":
                query = input("Enter your reprompt: ")
            case _:
                break


def main():
    parser = argparse.ArgumentParser(
        description="QQ: CLI command explainer and generator using LLMs"
    )
    parser.add_argument(
        "-g",
        "--generate",
        action="store_true",
        help="Generate a command based on description",
    )
    parser.add_argument(
        "--model",
        default="claude-3-sonnet-20240229",
        help="Model to use for completion",
    )
    parser.add_argument(
        "--temperature", type=float, default=0.5, help="Temperature for completion"
    )
    parser.add_argument(
        "--stream", action="store_true", default=True, help="Stream the output"
    )
    parser.add_argument(
        "query",
        nargs=argparse.REMAINDER,
        help="Command to explain or description to generate",
    )
    args = parser.parse_args()

    query = " ".join(args.query)

    # Import litellm only when needed
    import litellm

    llm = partial(
        litellm.completion,
        model=args.model,
        temperature=args.temperature,
        stream=args.stream,
    )

    if args.generate:
        generate(llm, query)
    else:
        explain(llm, query)


if __name__ == "__main__":
    main()
