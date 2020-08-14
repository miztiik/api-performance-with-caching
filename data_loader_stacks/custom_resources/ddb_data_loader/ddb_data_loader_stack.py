
from aws_cdk import aws_cloudformation as cfn
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as _logs

from aws_cdk import core


class GlobalArgs:
    """
    Helper to define global statics
    """

    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = "secure-api-with-throttling"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_08_03"
    MIZTIIK_SUPPORT_EMAIL = ["mystique@example.com", ]


class DdbDataLoaderStack(core.Construct):
    def __init__(self, scope: core.Construct, id: str, ** kwargs) -> None:
        super().__init__(scope, id)

        # Read Lambda Code:)
        try:
            with open("data_loader_stacks/custom_resources/ddb_data_loader/lambda_src/index.py",
                      encoding="utf-8",
                      mode="r"
                      ) as f:
                ddb_data_loader_fn_code = f.read()
        except OSError:
            print("Unable to read Lambda Function Code")
            raise

        # Create IAM Permission Statements that are required by the Lambda

        role_stmt1 = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=["*"],
            actions=[
                "dynamodb:PutItem",
                "dynamodb:DeleteItem",
                "dynamodb:UpdateItem",
            ]
        )
        role_stmt1.sid = "AllowLambdaToLoadItems"

        ddb_data_loader_fn = _lambda.SingletonFunction(
            self,
            "ddbDataLoaderSingleton",
            uuid=f"mystique133-0e2efcd4-3a29-e896f670",
            code=_lambda.InlineCode(
                ddb_data_loader_fn_code),
            handler="index.lambda_handler",
            timeout=core.Duration.seconds(12),
            runtime=_lambda.Runtime.PYTHON_3_7,
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": "INFO",
                "APP_ENV": "Production"
            },
            description="Load Data into DyanamoDB",
            function_name=f"ddbDataLoader-{id}"
        )

        ddb_data_loader_fn.add_to_role_policy(role_stmt1)

        # Cfn does NOT do a good job in cleaning it up when deleting the stack. Hence commenting this section
        """
        # Create Custom Log group
        ddb_data_loader_fn_lg = _logs.LogGroup(
            self,
            "ddb_data_loaderLogGroup",
            log_group_name=f"/aws/lambda/{ddb_data_loader_fn.function_name}",
            retention=_logs.RetentionDays.ONE_WEEK,
            removal_policy=core.RemovalPolicy.DESTROY
        )
        """

        ddb_data_loader = cfn.CustomResource(
            self,
            "ddb_data_loaderCustomResource",
            provider=cfn.CustomResourceProvider.lambda_(
                ddb_data_loader_fn
            ),
            properties=kwargs,
        )

        self.response = ddb_data_loader.get_att(
            "data_load_status").to_string()
