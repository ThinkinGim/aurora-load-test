from aws_cdk import (
    core,
    aws_ec2,
    aws_iam,
    aws_rds,
    aws_secretsmanager,
    aws_lambda,
)


class TestFunctionStack(core.Stack):
    
    def __init__(self, scope: core.Construct, id: str, 
            vpc: aws_ec2.Vpc, 
            db_secret: aws_secretsmanager.Secret,
            s3_bucket_name: str,
            **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        role_init = aws_iam.Role(self, 'test-func-init-role',
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com")
        )

        role_init.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaENIManagementAccess')
        )
        role_init.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')
        )
        role_init.add_to_policy(
            aws_iam.PolicyStatement(
                resources=[db_secret.secret_arn],
                actions=[
                    "secretsmanager:GetResourcePolicy",
                    "secretsmanager:GetSecretValue",
                    "secretsmanager:DescribeSecret",
                    "secretsmanager:ListSecretVersionIds"
                ]
            )
        )

        aurora_load_test_init = aws_lambda.Function(self, 'aurora_load_test_init',
            function_name='aurora_load_test_init',
            handler='aurora_load_test_init.init',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.asset('./app_stack/func_init'),
            role=role_init,
            timeout=core.Duration.seconds(900),
            allow_public_subnet=False,
            vpc=vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE),
            environment={
                'db_secret': db_secret.secret_name,
                's3_bucket_name': s3_bucket_name
            }
        )

        aurora_load_test_test = aws_lambda.Function(self, 'aurora_load_test_test',
            function_name='aurora_load_test_test',
            handler='aurora_load_test_test.test',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.asset('./app_stack/func_test'),
            role=role_init,
            timeout=core.Duration.seconds(900),
            allow_public_subnet=False,
            vpc=vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE),
            environment={
                'db_secret': db_secret.secret_name,
                's3_bucket_name': s3_bucket_name
            }
        )

        
