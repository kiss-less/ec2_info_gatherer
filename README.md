# EC2 Info Gatherer

## Overview
This script is designed to gather information about all the EC2 instances in the current region and group the result by AMI (Amazon Machine Image). It utilizes the AWS API to fetch details in batches, overcoming the API call limitations for AWS accounts with a large number of instances.

## Prerequisites
- Python 3.x
- Boto3 library
- AWS credentials configured (via environment variables, or AWS credentials file)

## Installation
1. Ensure that Python 3.x is installed on your system.
2. Install dependencies using pip:

`pip3 install -r requirements.txt`

## Usage
Run the script with the following command:

`python3 ec2_info_gatherer.py`


### Optional Arguments
- `-l`, `--log`: Set the logging level (default: ERROR). Available options: INFO, ERROR.
- `-b`, `--batch-limit`: Set the batch limit to N instances (default: 20). The value should be more than 5 to avoid AWS API call limitations.
- `-i`, `--output-indent`: Set the output indentation to X. (default: 4).

## Logging
The script provides logging functionality to track its progress and errors. The log level can be adjusted to display more or less information during execution.

## Batch Limit
The `--batch-limit` argument divides the API calls into batches, each limited to N instances, to efficiently manage the data retrieval process without hitting AWS API call limits.

## Error Handling
The script includes error handling to manage exceptions that may occur during the AWS API calls, ensuring that any issues are logged and can be addressed.

## Output
The output will be a JSON-formatted string that groups EC2 instance information by AMI, which can be redirected to a file or processed further as needed.

## Acknowledgments
- AWS documentation
- Boto3 library
