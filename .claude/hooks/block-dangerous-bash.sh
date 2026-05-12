#!/usr/bin/env bash
# block-dangerous-bash.sh
# Hook: PreToolUse — blocks dangerous Bash commands.
# Input: JSON on stdin with a "tool_input" field containing {"command": "..."}.

set -euo pipefail

# Read the hook input from stdin.
input=$(cat)

# Extract the command string using jq.
cmd=$(echo "$input" | jq -r '.tool_input.command // empty')

# Dangerous patterns to block.
dangerous_patterns=(
    "rm -rf"
    "rm -r /"
    "git push --force"
    "git push -f"
    "git reset --hard"
    "sudo"
)

for pattern in "${dangerous_patterns[@]}"; do
    if [[ "$cmd" == *"$pattern"* ]]; then
        echo "BLOCKED: Command contains dangerous pattern '$pattern'."
        exit 1
    fi
done

# Command is safe — allow.
exit 0
