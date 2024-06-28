#!/usr/bin/env python3

import argparse
import os
import platform
import subprocess
import sys
import tempfile
from functools import partial
from typing import Callable, Dict

import litellm

os.environ["LITELLM_LOG"] = "DEBUG"


# Check for required API keys
NEEDED_KEYS = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")
missing_keys = [key for key in NEEDED_KEYS if not os.getenv(key)]
if missing_keys:
    print(
        f"Error: The following API key(s) are not set: {', '.join(missing_keys)}",
        file=sys.stderr,
    )
    sys.exit(1)

EXPLAIN_PROMPT = """
You are an expert in explaining command-line operations across various operating systems and shells. Your task is to provide clear, concise, and accurate explanations of commands, pipelines, and scripts. Follow these guidelines:

<guidelines>
1. Break down the command into its constituent parts.
2. Format your output with the main command fragment at the beginning of the line and subsequent parts indented based on their role.
3. Print out the formatted command part and then an explanation of that command fragment separated by a hyphen, on the same line.
4. If colors are enabled, use subtle color codes to enhance readability. Apply different colors to commands, options, arguments, and other syntactic structures as appropriate. Be consistent but maintain clarity. Make sure the coloring is added correctly for being streamed to the output terminal.
5. For each part, describe its function, any options or flags used, and their effects.
6. If applicable, mention any potential side effects or important considerations.
7. Conclude with a one-line summary of the overall operation.
8. Use technical terminology where appropriate
9. Make sure your output is formatted correctly and carefully to be clear and visually appealing. Don't use excessive spacing or newlines, keep your output condensed, but keep different components of the output separate from one another with an extra newline, for example, the final command explanation.
10. If the shell supports colors, intelligently colorize your output, but if the shell does not, do not output any colors. 
    It is very important that if colors are disabled, you do not output colors, despite what the examples say.
11. Do not include <output></output> tags or special formatting tags like backticks. These are unnecessary on the terminal.
</guidelines>

<system_information>
Shell color support: :r:color_support
</system_information>

<examples>
<input>
find . -type f -name "*.txt" -exec sed -i 's/foo/bar/g' {} +
</input>
<output>
\033[1;34mfind\033[0m \033[1;32m.\033[0m - Start searching from the current directory
    \033[1;35m-type\033[0m \033[1;32mf\033[0m - Look for regular files only
    \033[1;35m-name\033[0m \033[1;33m"*.txt"\033[0m - Match files with names ending in .txt
    \033[1;35m-exec\033[0m \033[1;36msed\033[0m - Execute the following command for each matched file
        \033[1;35m-i\033[0m - Edit files in-place
        \033[1;33m's/foo/bar/g'\033[0m - Replace all occurrences of 'foo' with 'bar'
    \033[1;32m{} +\033[0m - Pass multiple filenames to sed efficiently
This command finds all .txt files in the current directory and its subdirectories, then replaces all occurrences of 'foo' with 'bar' in each file.
</output>
<input>
docker run --rm -d --name nginx -p 80:80 -v /host/path:/container/path nginx:latest
</input>
<output>
\033[1;34mdocker run\033[0m - Run a Docker container
    \033[1;35m--rm\033[0m - Automatically remove the container when it exits
    \033[1;35m-d\033[0m - Run the container in detached mode (in the background)
    \033[1;35m--name\033[0m \033[1;33mnginx\033[0m - Assign the name "nginx" to the container
    \033[1;35m-p\033[0m \033[1;33m80:80\033[0m - Map port 80 of the host to port 80 in the container
    \033[1;35m-v\033[0m \033[1;33m/host/path:/container/path\033[0m - Mount a volume, mapping /host/path on the host to /container/path in the container
    \033[1;36mnginx:latest\033[0m - Use the latest version of the nginx image
This command starts a detached nginx container named "nginx", mapping port 80 and a volume, using the latest nginx image.
</output>
<input>
grep -r '/opt/home' ~/.*(D.)
</input>
<output>
\033[1;34mgrep\033[0m - Search for patterns in files
    \033[1;35m-r\033[0m - Recursively search subdirectories
    \033[1;33m'/opt/home'\033[0m - The pattern to search for
    \033[1;36m~/.*(D.)\033[0m - Zsh glob pattern that matches all hidden files and directories in the home directory
This command searches for the string '/opt/home' in all hidden files and directories (dotfiles) in the user's home directory using Zsh-specific globbing.

Input: curl -s 'https://api.github.com/repos/stedolan/jq/commits?per_page=5' | jq -r '.[] | "\\(.commit.author.date) \\(.commit.author.name)"'
Output:
\033[1;34mcurl\033[0m - Command-line tool for transferring data using various protocols
    \033[1;35m-s\033[0m - Silent mode, don't show progress meter or error messages
    \033[1;33m'https://api.github.com/repos/stedolan/jq/commits?per_page=5'\033[0m - URL of the GitHub API endpoint for jq repository commits, limited to 5 per page
\033[1;36m|\033[0m - Pipe the output of curl to the next command
\033[1;34mjq\033[0m - Command-line JSON processor
    \033[1;35m-r\033[0m - Output raw strings, not JSON texts
    \033[1;33m'.[] | "\\(.commit.author.date) \\(.commit.author.name)"'\033[0m - JQ filter:
        \033[1;33m.[]\033[0m - Iterate over each item in the array
        \033[1;33m| "\\(.commit.author.date) \\(.commit.author.name)"\033[0m - For each commit, print the author's date and name
This command fetches the last 5 commits from the jq GitHub repository and extracts the date and author name for each commit.
</output>
<input>
http -a username:password POST https://api.example.com/v1/users name=John age:=30 roles:='["admin", "user"]'
</input>
<output>
\033[1;34mhttp\033[0m - Command-line HTTP client (part of HTTPie)
    \033[1;35m-a\033[0m \033[1;33musername:password\033[0m - Specify basic authentication credentials
    \033[1;35mPOST\033[0m - Use HTTP POST method
    \033[1;33mhttps://api.example.com/v1/users\033[0m - URL of the API endpoint
    \033[1;36mname=John\033[0m - Set 'name' field to 'John' (sent as form data)
    \033[1;36mage:=30\033[0m - Set 'age' field to integer 30 (`:=` for non-string data types)
    \033[1;36mroles:='["admin", "user"]'\033[0m - Set 'roles' field to a JSON array (`:=` for JSON data)
This command sends a POST request to create a new user with the given name, age, and roles, using basic authentication.
</output>
</examples>
"""

GENERATE_PROMPT = """
You are an expert in generating command-line operations across various operating systems and shells. Your task is to create efficient, effective, and safe commands based on user descriptions. 

Current system information:
- Operating System: :r:os (Version: :r:os_version)
- Shell: :r:shell
- Python Version: :r:python_version
- User: :r:user
- Home Directory: :r:home

Shell color support: :r:color_support. If the shell supports colors, intelligently colorize your output, but if the shell does not, do not output colors.

Follow these guidelines:

1. Output only the command or script, wrapped in <command></command> tags.
2. Ensure the command is correct, efficient, and follows best practices for the current operating system and shell.
3. Use appropriate flags, options, and syntax for the current environment.
4. Incorporate error handling and safety checks where appropriate.
5. For complex operations, consider using multiple commands connected with pipes or creating a small script.
6. When working with dotfiles or hidden files in Zsh, use the glob pattern ~/.*(D.) to match all hidden files and directories in the home directory.
7. Tailor your commands to the specific OS and shell environment provided above.

Examples:

Input: Find all Python files modified in the last 7 days and create a zip archive of them
Output: <command>find . -type f -name "*.py" -mtime -7 -print0 | xargs -0 zip updated_python_files.zip</command>

Input: Monitor system resource usage, logging CPU, memory, and disk usage every 5 seconds to a file named system_usage.log
Output: <command>while true; do echo "$(date): $(top -bn1 | grep load | awk '{printf "CPU Load: %.2f", $(NF-2)}') $(free -m | awk 'NR==2{printf " Memory Usage: %s/%sMB %.2f%%", $3,$2,$3*100/$2 }') $(df -h | awk '$NF=="/"{printf " Disk Usage: %d/%dGB %s", $3,$2,$5}')"; sleep 5; done >> system_usage.log</command>

Input: Create a bash script that backs up all .jpg files in the current directory to a timestamped folder in /backups, compresses the folder, and deletes files older than 30 days
Output: <command>cat << 'EOF' > backup_script.sh
#!/bin/bash
set -e

BACKUP_DIR="/backups/photos_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

find . -maxdepth 1 -type f -name "*.jpg" -exec cp {} "$BACKUP_DIR" \\;

tar czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

find /backups -type f -name "photos_*.tar.gz" -mtime +30 -delete

echo "Backup completed successfully"
EOF
chmod +x backup_script.sh</command>

Input: Set up a cron job to run a Python script every day at 3 AM
Output: <command>(crontab -l 2>/dev/null; echo "0 3 * * * /usr/bin/python3 /path/to/your/script.py") | crontab -</command>

Input: Create a Docker command to run a PostgreSQL container with a custom configuration, set a password, and map to a local volume
Output: <command>docker run -d --name postgres_db -e POSTGRES_PASSWORD=mysecretpassword -v /path/to/local/data:/var/lib/postgresql/data -v /path/to/custom/postgresql.conf:/etc/postgresql/postgresql.conf postgres:latest -c 'config_file=/etc/postgresql/postgresql.conf'</command>

Input: Search for all instances of '/opt/home' in my dotfiles using Zsh
Output: <command>grep -r '/opt/home' ~/.*(D.)</command>
"""


def supports_color(enabled: bool):
    """
    Returns True if the running system's terminal supports color,
    and False otherwise.
    """
    if enabled:
        plat = sys.platform
        supported_platform = plat != "Pocket PC" and (
            plat != "win32" or "ANSICON" in os.environ
        )
        is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
        return supported_platform and is_a_tty
    return False


def imbue(prompt: str, info: Dict[str, str]) -> str:
    for key, value in info.items():
        prompt = prompt.replace(f":r:{key}", str(value), 1)
    return prompt


def explain(llm: Callable, query: str, args: dict) -> None:
    system_prompt = imbue(
        EXPLAIN_PROMPT,
        {"color_support": "enabled" if supports_color(args.color) else "disabled"},
    )

    if args.debug:
        print("\033[1;31mDEBUG: imbued system_prompt\033[0m")
        print(system_prompt)
        print("\033[1;31mDEBUG: repr(imbued system_prompt)\033[0m")
        print(repr(system_prompt))

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ]

    buffer = []
    for chunk in llm(messages=messages):
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    #         buffer.append(content)
    #         if "\n" in content:
    #             head, tail = content.split("\n", 1)
    #             buffer.append(head)
    #             print("".join(buffer), end="\n", flush=True)
    #             buffer = [tail]
    # if buffer:
    #     print("".join(buffer), end="", flush=True)
    print()  # Print a newline at the end


def generate(llm: Callable, query: str, args: dict) -> None:
    color_support = supports_color(args.color)
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "shell": os.environ.get("SHELL", "Unknown"),
        "python_version": platform.python_version(),
        "user": os.environ.get("USER", "Unknown"),
        "home": os.environ.get("HOME", "Unknown"),
    }
    if not args.env:
        system_info = {k: "Unknown" for k in system_info.keys()}

    system_info["color_support"] = color_support
    system_prompt = imbue(GENERATE_PROMPT, system_info)
    if args.debug:
        print("\033[1;34mgenerate system prompt\033[0m")
        print(system_prompt)

    messages = [
        {"role": "system", "content": system_prompt},
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

        command_start = result.find("<command>") + len("<command>")
        command_end = result.find("</command>")
        command = result[command_start:command_end].strip()
        # clean it up a little
        result = result.replace("<command>", "").replace("</command>", "")

        print(f"Command to execute: {command}")
        print("e(x)ec / (e)dit / (r)etry / (q)uit: ", end="")
        choice = input().strip().lower()
        match choice:
            case "x":
                # bye!
                os.execlp("zsh", "zsh", "-c", command)
            case "e":
                with tempfile.NamedTemporaryFile(
                    mode="w+", suffix=".txt", delete=False
                ) as tmp:
                    tmp.write(result)
                    tmp_filename = tmp.name

                try:
                    subprocess.run(["sh", "-c", "$EDITOR", tmp_filename], check=True)
                    with open(tmp_filename, "r") as tmp:
                        query = tmp.read().strip()
                finally:
                    os.unlink(tmp_filename)
            case "r":
                query = input("Enter your reprompt: ")
            case "q" | _:
                break


def main():
    parser = argparse.ArgumentParser(
        description="qq: cli explainer and generator using LLMs"
    )
    parser.add_argument(
        "-g",
        "--generate",
        action="store_true",
        help="Generate a command based on description",
    )
    parser.add_argument(
        "-m",
        "--model",
        default="claude-3-sonnet-20240229",
        help="Model to use for completion",
    )
    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        default=0.5,
        help="Temperature for completion",
    )
    parser.add_argument(
        "--stream", action="store_true", default=True, help="Stream the output"
    )
    parser.add_argument(
        "--env",
        action="store_true",
        help="Include environment information in command generation",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode for more verbose output",
    )
    parser.add_argument(
        "--color",
        action="store_false",
        help="Enable color output in the terminal",
    )
    parser.add_argument(
        "query",
        nargs=argparse.REMAINDER,
        help="Command to explain or description to generate",
    )
    args = parser.parse_args()

    query = " ".join(args.query)

    try:
        # we'll get rid of this eventually
        pass
    except ImportError:
        print("Error: litellm was not found.")
        sys.exit(1)

    llm = partial(
        litellm.completion,
        model=args.model,
        temperature=args.temperature,
        stream=args.stream,
    )

    try:
        if args.generate:
            generate(llm, query, args)
        else:
            explain(llm, query, args)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
