from aws_cdk import (
    core,
    aws_ec2,
)

from app_stack.vpc_stack import VpcStack
from app_stack.controller_stack import ControllerStack
from app_stack.rds_demo_stack import RdsDemoStack
from app_stack.test_function_stack import TestFunctionStack

class DeployStage(core.Stage):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc_stack = VpcStack(self, 'vpc')

        ControllerStack(self, 'workspace', vpc=vpc_stack.vpc)

        db = RdsDemoStack(self, 'db', vpc=vpc_stack.vpc)

        TestFunctionStack(self, 'func', vpc=vpc_stack.vpc, db_secret=db.db_secret, s3_bucket_name=db.s3_bucket_name)
