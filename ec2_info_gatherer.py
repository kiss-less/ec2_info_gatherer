import boto3, logging, json
from collections import defaultdict
from argparse import ArgumentParser


LOG_LEVELS = ["INFO", "ERROR"]

def verify_args(args):
    numeric_log_level = getattr(logging, args.log.upper(), None)

    if not isinstance(numeric_log_level, int):
        logging.error(f"Invalid log level: {args.log.upper()}. It should be one of {LOG_LEVELS}")
        exit(1)
    
    # The AWS API expects a value greater than 5 for the maxResults parameter when calling the DescribeInstances operation
    if args.batch_limit <= 5:
        logging.error(f"Invalid value of the -b (--batch-limit) argument! It should be more than 5")
        exit(1)

    logging.basicConfig(level=numeric_log_level, format="%(asctime)s - %(levelname)s - %(message)s")

def gather_ec2_info(args):
    session = boto3.session.Session()
    ec2_client = session.client("ec2")

    logging.info(f"Gathering info about all ec2 instances in the {session.region_name} region in batches of {args.batch_limit} item(s) per request with output indentation of {args.output_indent}")
    result = defaultdict(lambda: {"ImageDescription": None, "ImageName": None, "ImageLocation": None, "OwnerId": None, "InstanceIds": []})
    try:
        paginator = ec2_client.get_paginator("describe_instances")
    except boto3.exceptions.Boto3Error as e:
        logging.error(f"EC2 Instances could not be described: {e}")
        exit(1)

    page_iterator = paginator.paginate(PaginationConfig={"PageSize": args.batch_limit})

    for idx, page in enumerate(page_iterator):
        logging.info(f"Processing batch {idx + 1}")
        for reservation in page["Reservations"]:
            for instance in reservation["Instances"]:
                ami_id = instance["ImageId"]
                if ami_id not in result:
                    try:
                        # Since we are passing a single ImageId, we are only interested in the first element of the list
                        ami_info = ec2_client.describe_images(ImageIds=[ami_id])["Images"][0]
                        result[ami_id]["ImageDescription"] = ami_info.get("Description", None)
                        result[ami_id]["ImageName"] = ami_info.get("Name", None)
                        result[ami_id]["ImageLocation"] = ami_info.get("ImageLocation", None)
                        result[ami_id]["OwnerId"] = ami_info.get("OwnerId", None)
                    except boto3.exceptions.Boto3Error as e:
                        logging.error(f"AMI information for {ami_id} could not be retrieved: {e}")
                        result[ami_id]["ImageDescription"] = None
                        result[ami_id]["ImageName"] = None
                        result[ami_id]["ImageLocation"] = None
                        result[ami_id]["OwnerId"] = None
                result[ami_id]["InstanceIds"].append(instance["InstanceId"])
        idx += 1

    result = {ami_id: ami_data for ami_id, ami_data in result.items() if ami_data["InstanceIds"]}
    logging.info(f"Info has been successfully gathered")

    print(json.dumps(result, indent=args.output_indent))


def main():
    parser = ArgumentParser(description="This script gathers ec2 instances information and groups it by AMI")
    parser.add_argument("-l", "--log", metavar="LOG_LEVEL", type=str, default="INFO",
        help=f"This argument sets the logging level, where LOG_LEVEL should be one of {LOG_LEVELS}. Default is INFO")
    parser.add_argument("-b", "--batch-limit", metavar="N", type=int, default=20,
        help="""
This argument divides the API calls into batches, each limited to N instances 
(where N should be more than 5), to avoid AWS API call limitations in accounts 
with a large number of instances. Default is 20
""")
    parser.add_argument("-i", "--output-indent", metavar="X", type=int, default=4,
        help="This argument sets the output indentation to X. The default is 4")
    args = parser.parse_args()

    verify_args(args)
    gather_ec2_info(args)

if __name__ == "__main__":
    main()
