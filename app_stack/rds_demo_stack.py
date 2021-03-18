from aws_cdk import (
    core,
    aws_ec2,
    aws_iam,
    aws_rds,
    aws_s3,
)

class RdsDemoStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc: aws_ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        demo_s3 = aws_s3.Bucket(self, 'rds-demo',
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        subnet_sel = aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.ISOLATED)

        db_subnet_group = aws_rds.SubnetGroup(self, 'rds-demo-sbg',
            description='rds demo subnet group',
            vpc=vpc,
            removal_policy=core.RemovalPolicy.DESTROY,
            vpc_subnets=subnet_sel
        )

        vpc.add_s3_endpoint('rds-s3endpoint',
            subnets=[subnet_sel]
        )

        role_s3_db = aws_iam.Role(self, 'role_db_s3',
            assumed_by=aws_iam.ServicePrincipal("rds.amazonaws.com")
        )

        role_s3_db.add_to_policy(
            aws_iam.PolicyStatement(
                resources=[
                    demo_s3.bucket_arn,
                    f"{demo_s3.bucket_arn}/*"
                ],
                actions=['s3:*']
            )
        )

        db_security_group = aws_ec2.SecurityGroup(self, 'rds-sg',
            vpc=vpc
        )

        db_security_group.add_ingress_rule(
            peer=aws_ec2.Peer.ipv4('10.254.0.0/16'),
            connection=aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="to allow from the vpc internal",
                from_port=3306,
                to_port=3306
            )
        )

        param_group = aws_rds.ParameterGroup(self, 'rds-param',
            engine=aws_rds.DatabaseClusterEngine.AURORA_MYSQL
        )
        param_group.add_parameter("aurora_load_from_s3_role", role_s3_db.role_arn)
        param_group.add_parameter("aurora_select_into_s3_role", role_s3_db.role_arn)
        param_group.add_parameter("aws_default_s3_role", role_s3_db.role_arn)

        db_cluster = aws_rds.DatabaseCluster(self, 'rds-demo-cluster',
            engine=aws_rds.DatabaseClusterEngine.aurora_mysql(version=aws_rds.AuroraMysqlEngineVersion.VER_2_07_1),
            instance_props=aws_rds.InstanceProps(
                vpc=vpc,
                instance_type=aws_ec2.InstanceType.of(instance_class=aws_ec2.InstanceClass.BURSTABLE3, instance_size=aws_ec2.InstanceSize.MEDIUM),
                security_groups=[db_security_group]
            ),
            instances=1,
            subnet_group=db_subnet_group,
            s3_import_role=role_s3_db,
            parameter_group=param_group,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        self.db_secret = db_cluster.secret
        self.s3_bucket_name = demo_s3.bucket_name
