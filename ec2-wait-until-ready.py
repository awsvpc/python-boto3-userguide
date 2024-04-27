def get_subnet_tier(subnet_id):
    ec2 = boto3.client('ec2')
    subnet = ec2.describe_subnets(SubnetIds=[subnet_id])['Subnets'][0]
    for tag in subnet['Tags']:
        if tag['Key'] == 'TIER':
            return tag['Value']
    return None
def get_instance_ip(instance_id):
    ec2 = boto3.client('ec2', region_name='us-east-1')
    print("Querying EC2 management IP..")
    instance = ec2.describe_instances(InstanceIds=[instance_id])
    reservations = instance['Reservations']
    for reservation in reservations:
        for instance in reservation['Instances']:
            enis = instance['NetworkInterfaces']
            for eni in enis:
                subnet_id = eni['SubnetId']
                tier_tag = get_subnet_tier(subnet_id)
                if tier_tag == 'MGT':
                    return eni['PrivateIpAddress']
    return None
def wait_until_deploy_complete(instance_id, timeout=180):
    try:
        ec2 = boto3.client('ec2')
        start_time = time.time()
        time.sleep(timeout)
        print("Querying ec2 deploy completion status, Waiting..")
        while True:
            response = ec2.describe_instances(InstanceIds=[instance_id])
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    tags = instance['Tags']
                    status = str(''.join([tag['Value'] for tag in tags if((tag['Key'].casefold()).__eq__('DeployStatus'.casefold()))]))
                    if status == 'Complete':
                        print("Instance DeployStatus completed")
                        return True
            if time.time() - start_time >= 3600:
                print("Timeout waiting for DeployStatus to be complete.")
                sys.exit(1)
            time.sleep(timeout)
            print(f"Waiting for DeployStatus tag on Instance Id: {instance_id}")
    except botocore.exceptions.ClientError as error:
        print(f"Error : {error.response['Error']}")
        sys.exit(1)
    except Exception as error:
        print("Error: {} while querying DeployStatus tag".format(error))
        sys.exit(1)
def wait_until_reachable(instance_id, timeout=120):
    try:
        ec2 = boto3.client('ec2')
        start_time = time.time()
        time.sleep(timeout)
        print("Querying ec2 reachability, Waiting..")
        while True:
            response = ec2.describe_instance_status(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}],
                InstanceIds=[instance_id]
            )
            if len(response['InstanceStatuses']) > 0:
                status = response['InstanceStatuses'][0]
                if status['InstanceStatus']['Status'] == 'ok' and status['SystemStatus']['Status'] == 'ok':
                    print("InstanceStatus check passed")
                    if wait_until_deploy_complete(instance_id):
                        return True
            if time.time() - start_time >= 3600:
                print("Timeout waiting for InstanceStatus check.")
                sys.exit(1)
            time.sleep(timeout)
            print(f"Waiting for Instance Id: {instance_id} to become online")
    except Exception as error:
        if error.response['Error']['Code'] == "InvalidInstanceID.NotFound":
            print(f"Error: {error.response['Error']['Message']}. Exiting")
            sys.exit(1)
        else:
            print("Error: {} while querying InstanceStatus check".format(error))
            sys.exit(1)
