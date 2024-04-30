import boto3
import csv
import concurrent.futures

client = boto3.client("ec2", region_name="us-east-2")


def open_file():
    with open("new.csv") as file_obj:
        reader_obj = csv.reader(file_obj)
        error_eni = []
        with open("error.csv", "w") as f:
            writer = csv.writer(f)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_eni = {
                    executor.submit(process_eni, row[0]): row[0] for row in reader_obj
                }
                for future in concurrent.futures.as_completed(future_to_eni):
                    eni, success = future.result()
                    if not success:
                        error_eni.append(eni)
            writer.writerow(error_eni)
            print(error_eni)


def process_eni(eni):
    try:
        response = client.describe_network_interfaces(NetworkInterfaceIds=[eni])
        vpcID = response["NetworkInterfaces"][0]["VpcId"]
        vpc_response = client.describe_vpcs(VpcIds=[vpcID])
        for tags in vpc_response["Vpcs"][0]["Tags"]:
            if tags["Key"] in ["client", "customer", "environment"]:
                create_tags(eni, tags["Key"], tags["Value"])
                # print(tags["Key"])
                # print(tags["Value"])
        return eni, True
    except Exception as e:
        return eni, False


def create_tags(eni, k, v):
    client.create_tags(Resources=[eni], Tags=[{"Key": k, "Value": v}])
    print("done")


open_file()
