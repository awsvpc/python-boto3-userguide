import boto3
import json

def assume_role_and_check_trust_policy(role_arn):
    try:
        # Assume the role
        sts_client = boto3.client('sts')
        response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName='AssumeRoleSession')
        credentials = response['Credentials']
        
        # Create a session using the assumed role's temporary credentials
        session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        
        # Create an IAM client using the assumed role session
        iam_client = session.client('iam')
        
        # Get the trust policy for the specified role
        response = iam_client.get_role(RoleName=role_arn.split('/')[-1])
        trust_policy = json.loads(response['Role']['AssumeRolePolicyDocument'])
        
        # Check if the trust policy contains the specified ARN pattern
        for statement in trust_policy['Statement']:
            if 'Principal' in statement and 'AWS' in statement['Principal'] and 'arn:aws:account:' in statement['Principal']['AWS']:
                print("Trust policy for role '{}' contains the specified ARN pattern.".format(role_arn))
                return True
        
        print("Trust policy for role '{}' does not contain the specified ARN pattern.".format(role_arn))
        return False
        
    except Exception as e:
        print("Error occurred: {}".format(str(e)))
        return False

if __name__ == "__main__":
    iam_role_list = [
        "arn:aws:iam::123456789012:role/role1",
        "arn:aws:iam::123456789012:role/role2",
        "arn:aws:iam::123456789012:role/role3"
    ]
    
    for role_arn in iam_role_list:
        assume_role_and_check_trust_policy(role_arn)
