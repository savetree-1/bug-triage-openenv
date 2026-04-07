#!/usr/bin/env bash
# deployment helper
set -e

echo "Logging into Hugging Face..."
huggingface-cli login --token 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 --add-to-git-credential

USERNAME=$(huggingface-cli whoami | head -n 1)
echo "Logged in as: $USERNAME"

echo "Pushing Bug Triage environment to Hugging Face Spaces..."
openenv push --repo-id "$USERNAME/bug-triage-openenv"

echo "Deployment submitted! Check your Hugging Face profile to see the building Space."
