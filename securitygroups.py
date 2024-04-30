import boto3
import csv
import concurrent.futures

client = boto3.client("ec2", region_name="us-east-2")


def open_file():
    with open("new.csv") as file_obj:
        reader_obj = csv.reader(file_obj)
        error_sg = []
        with open("error.csv", "w") as f:
            writer = csv.writer(f)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_sg = {
                    executor.submit(process_sg, row[0]): row[0] for row in reader_obj
                }
                for future in concurrent.futures.as_completed(future_to_sg):
                    sg, success = future.result()
                    if not success:
                        error_sg.append(sg)
            writer.writerow(error_sg)
            print("Error security groups written to error.csv")


def process_sg(sg):
    try:
        sg_response = client.describe_security_groups(GroupIds=[sg])
        if not sg_response["SecurityGroups"]:
            print(f"Security group {sg} not found.")
            return sg, False

        vpcID = sg_response["SecurityGroups"][0]["VpcId"]
        vpc_response = client.describe_vpcs(VpcIds=[vpcID])

        for tags in vpc_response["Vpcs"][0].get("Tags", []):
            if tags["Key"] in ["client", "customer", "application", "environment"]:
                create_tags(sg, tags["Key"], tags["Value"])
                print(tags["Key"])
                print(tags["Value"])
        return sg, True
    except Exception as e:
        print(f"Error processing security group {sg}: {str(e)}")
        return sg, False


def create_tags(sg, k, v):
    try:
        client.create_tags(Resources=[sg], Tags=[{"Key": k, "Value": v}])
        print(f"Added tag {k}={v} to security group {sg}")
    except Exception as e:
        print(f"Error adding tag to security group {sg}: {str(e)}")


open_file()
