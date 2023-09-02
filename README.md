# GitHub Repo Viewer Script

## Description

This script fetches details about GitHub repositories of a specified organization using the `gh` command-line tool. It outputs the information in a CSV file. 

## Requirements

- Python 3.x
- `gh` CLI tool installed and authenticated
- `jq` for JSON parsing (optional)

## Usage

```bash
python fetch-repos.py <organization_name> [--limit <limit>]
