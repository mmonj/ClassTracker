#!/bin/bash

set -e

ENV_FILE=".env.dev"

# Find all *-compose*.yml files in the current directory
compose_files=(./*-compose*.yml)
num_files=${#compose_files[@]}

if [ "$num_files" -eq 0 ]; then
	echo "No .yml files found in current directory."
	exit 1
elif [ "$num_files" -eq 1 ]; then
	compose_file="${compose_files[0]}"
else
	echo "Multiple .yml files found. Please select one:"
	select compose_file in "${compose_files[@]}"; do
		if [ -n "$compose_file" ]; then
			break
		fi
	done
fi

echo docker compose -f "$compose_file" --env-file "$ENV_FILE" "$@"
docker compose -f "$compose_file" --env-file "$ENV_FILE" "$@"
