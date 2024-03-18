import boto3
import csv
import concurrent.futures

client = boto3.client("ec2", region_name="us-west-2")


def open_file():
    with open("new.csv") as file_obj:
        reader_obj = csv.reader(file_obj)
        error_ec2 = []
        with open("error.csv", "w") as f:
            writer = csv.writer(f)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_ec2 = {
                    executor.submit(process_ec2, row[0]): row[0] for row in reader_obj
                }
                for future in concurrent.futures.as_completed(future_to_ec2):
                    ec2, success = future.result()
                    if not success:
                        error_ec2.append(ec2)
            writer.writerow(error_ec2)
            print(error_ec2)


def process_ec2(ec2):
    try:
        response = client.describe_instances(InstanceIds=[ec2])
        vpcID = response["Reservations"][0]["Instances"][0]["VpcId"]
        vpc_response = client.describe_vpcs(VpcIds=[vpcID])
        for tags in vpc_response["Vpcs"][0]["Tags"]:
            if tags["Key"] in ["client", "customer"]:
                create_tags(ec2, tags["Key"], tags["Value"])
                print(tags["Key"])
                print(tags["Value"])
        return ec2, True
    except Exception as e:
        return ec2, False


def create_tags(ec2, k, v):
    client.create_tags(Resources=[ec2], Tags=[{"Key": k, "Value": v}])
    print("done")


open_file()
