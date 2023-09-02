import subprocess
import json
import os
import argparse
import csv

# Helper function to flatten JSON
def flatten_json(json_object, parent_key='', separator='.'):
    items = {}
    for key, value in json_object.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        if isinstance(value, dict):
            items.update(flatten_json(value, new_key, separator=separator))
        elif isinstance(value, list):
            items[new_key] = json.dumps(value)
        else:
            items[new_key] = value
    return items

# Function to run shell command and return the output
def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    if result.returncode != 0:
        print(f"Command failed with error: {result.stderr}")
    return result.stdout

# Argument parsing
parser = argparse.ArgumentParser(description='List GitHub repos for a given organization.')
parser.add_argument('organization', type=str, help='Name of the GitHub organization')
parser.add_argument('--limit', type=int, default=100, help='Limit for the number of repos to fetch')
args = parser.parse_args()
organization = args.organization
limit = args.limit

# Path to the cache file
cache_file_path = f'repo_list_cache_{organization}_{limit}.json'

# Check if the cache file exists
if os.path.exists(cache_file_path):
    # Load the cached repo list from file
    with open(cache_file_path, 'r') as cache_file:
        repo_list_json_str = cache_file.read()
else:
    # Get list of all repos in the specified organization
    repo_list_command = f"gh repo list --limit {limit} {organization} --json 'nameWithOwner'"
    repo_list_json_str = run_command(repo_list_command)
    
    # Cache the repo list to file
    with open(cache_file_path, 'w') as cache_file:
        cache_file.write(repo_list_json_str)

# Parse the JSON output
try:
    repo_list = json.loads(repo_list_json_str)
except json.JSONDecodeError as e:
    print(f"Failed to decode JSON: {e}")
    exit(1)

# Initialize CSV writer and header variable
csv_file_name = f'repo_details_{organization}.csv'
csv_file = open(csv_file_name, 'w', newline='')
csv_writer = csv.writer(csv_file)
header = None

# Write repo details
for repo in repo_list:
    repo_name_with_owner = repo.get("nameWithOwner", "")
    if repo_name_with_owner:
        print(f"Fetching details for {repo_name_with_owner}...")
        repo_view_command = f"gh repo view {repo_name_with_owner} --json 'codeOfConduct,contactLinks,createdAt,defaultBranchRef,deleteBranchOnMerge,description,diskUsage,forkCount,hasDiscussionsEnabled,hasIssuesEnabled,hasProjectsEnabled,hasWikiEnabled,homepageUrl,id,isArchived,isBlankIssuesEnabled,isEmpty,isFork,isInOrganization,isMirror,isPrivate,isSecurityPolicyEnabled,isTemplate,isUserConfigurationRepository,issueTemplates,issues,languages,latestRelease,licenseInfo,mergeCommitAllowed,milestones,mirrorUrl,name,nameWithOwner,openGraphImageUrl,owner,parent,primaryLanguage,projects,pullRequestTemplates,pullRequests,pushedAt,rebaseMergeAllowed,repositoryTopics,securityPolicyUrl,squashMergeAllowed,sshUrl,stargazerCount,templateRepository,updatedAt,url,usesCustomOpenGraphImage,visibility'"
        repo_view_json_str = run_command(repo_view_command)
        try:
            repo_view = json.loads(repo_view_json_str)
            # Flatten the repo_view JSON and write it to CSV
            flattened_repo_view = flatten_json(repo_view)            
            
            # Determine and write headers if this is the first repo_view
            if header is None:
                header = list(flattened_repo_view.keys())
                csv_writer.writerow(header)

            csv_writer.writerow([flattened_repo_view.get(col, '') for col in header])
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON for {repo_name_with_owner}: {e}")

# Close the CSV file
csv_file.close()

