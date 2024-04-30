import boto3
import csv
import concurrent.futures

client = boto3.client("ec2", region_name="us-east-2")


def open_file():
    with open("new.csv") as file_obj:
        reader_obj = csv.reader(file_obj)
        error_sn = []
        with open("error.csv", "w") as f:
            writer = csv.writer(f)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_sn = {
                    executor.submit(process_sn, row[0]): row[0] for row in reader_obj
                }
                for future in concurrent.futures.as_completed(future_to_sn):
                    sn, success = future.result()
                    if not success:
                        error_sn.append(sn)
            writer.writerow(error_sn)
            print("Error subnets  written to error.csv")


def process_sn(sn):
    try:
        sn_response = client.describe_subnets(SubnetIds=[sn])
        if not sn_response["Subnets"]:
            print(f"Subnets {sn} not found.")
            return sn, False

        vpcID = sn_response["Subnets"][0]["VpcId"]
        vpc_response = client.describe_vpcs(VpcIds=[vpcID])

        for tags in vpc_response["Vpcs"][0].get("Tags", []):
            if tags["Key"] in ["client", "customer", "application", "environment"]:
                create_tags(sn, tags["Key"], tags["Value"])
                print(tags["Key"])
                print(tags["Value"])
        return sn, True
    except Exception as e:
        print(f"Error processing security group {sn}: {str(e)}")
        return sn, False


def create_tags(sn, k, v):
    try:
        client.create_tags(Resources=[sn], Tags=[{"Key": k, "Value": v}])
        print(f"Added tag {k}={v} to security group {sn}")
    except Exception as e:
        print(f"Error adding tag to security group {sn}: {str(e)}")


open_file()
