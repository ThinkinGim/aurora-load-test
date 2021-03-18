from aws_cdk import (
    core,
    aws_ec2,
    aws_iam,
)

with open("./app_stack/user_data/user_data.sh") as f:
    user_data = f.read()

class ControllerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc: aws_ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        core.CfnOutput(self,'vpc_name',value=vpc.to_string())

        instance_role = aws_iam.Role(self, 'controller-role',
            role_name='controller-role',
            managed_policies=[
                aws_iam.ManagedPolicy.from_managed_policy_arn(self,'ssm_instance_core','arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'),
                aws_iam.ManagedPolicy.from_managed_policy_arn(self,'cloudwatch_agnet','arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy')
            ],
            assumed_by=aws_iam.ServicePrincipal('ec2.amazonaws.com')
        )

        aws_ec2.Instance(self, 'kube-control',
            instance_type=aws_ec2.InstanceType(instance_type_identifier="t3.micro"),
            machine_image=aws_ec2.AmazonLinuxImage(generation=aws_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            instance_name="demo-controller",
            role=instance_role,
            vpc=vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE),
            user_data=aws_ec2.UserData.custom(user_data)
        )

