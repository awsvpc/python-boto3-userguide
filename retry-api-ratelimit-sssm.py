import boto3
import time

def send_command(instance_id, command_document_name, params):
    try:
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName=command_document_name,
            Parameters=params
        )
        command_id = response['Command']['CommandId']
        return command_id, None
    except Exception as e:
        return None, e

def execute_commands(instance_ids, command_document_name, params):
    for instance_id in instance_ids:
        retries = 2
        while retries >= 0:
            command_id, error = send_command(instance_id, command_document_name, params)
            if error:
                if 'ThrottlingException' in str(error) or 'RequestLimitExceeded' in str(error):
                    print(f"Throttling or API limit exceeded for instance {instance_id}. Retrying in 5 seconds...")
                    time.sleep(5)
                    retries -= 1
                else:
                    print(f"Failed to send command to instance {instance_id}: {error}")
                    break
            else:
                print(f"Command sent successfully to instance {instance_id}. Command ID: {command_id}")
                break

if __name__ == "__main__":
    instance_ids = ["instance_id1", "instance_id2"]  # Replace with your instance IDs
    command_document_name = "AWS-RunShellScript"  # Replace with your command document name
    params = {"commands": ["your_command_here"]}  # Replace with your command parameters

    ssm = boto3.client('ssm', region_name='your_region')  # Replace 'your_region' with your AWS region

    execute_commands(instance_ids, command_document_name, params)
