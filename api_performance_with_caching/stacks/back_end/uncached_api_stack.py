import os

from aws_cdk import aws_apigateway as _apigw
from aws_cdk import aws_dynamodb as _dynamodb
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as _logs
from aws_cdk import core

from data_loader_stacks.custom_resources.ddb_data_loader.ddb_data_loader_stack import DdbDataLoaderStack


class GlobalArgs:
    """
    Helper to define global statics
    """

    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = "api-performance-with-caching"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_08_11"
    MIZTIIK_SUPPORT_EMAIL = ["mystique@example.com", ]


class UncachedApiStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        stack_log_level: str,
        back_end_api_name: str,
        back_end_api_datastore_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # DynamoDB: Key-Value Database):
        if not back_end_api_datastore_name:
            back_end_api_datastore_name = f"{GlobalArgs.REPO_NAME}-api-datastore"

        self.ddb_table_01 = _dynamodb.Table(
            self,
            "apiPerformanceWithCaching",
            partition_key=_dynamodb.Attribute(
                name="id",
                type=_dynamodb.AttributeType.STRING
            ),
            read_capacity=20,
            write_capacity=20,
            table_name=f"{back_end_api_datastore_name}-{id}",
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # Let us use our Cfn Custom Resource to load data into our dynamodb table.
        data_loader_status = DdbDataLoaderStack(
            self,
            "unCachedApiDdbLoader",
            Ddb_table_name=self.ddb_table_01.table_name
        )

        # Read Lambda Code):
        try:
            with open("api_performance_with_caching/stacks/back_end/lambda_src/serverless_greeter.py", mode="r") as f:
                greeter_fn_code = f.read()
        except OSError as e:
            print("Unable to read Lambda Function Code")
            raise e

        greeter_fn = _lambda.Function(
            self,
            "greeterFn",
            function_name=f"greeter_fn_{id}",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="index.lambda_handler",
            code=_lambda.InlineCode(greeter_fn_code),
            timeout=core.Duration.seconds(10),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": f"{stack_log_level}",
                "Environment": "Production",
                "DDB_TABLE_NAME": self.ddb_table_01.table_name,
                "RANDOM_SLEEP_SECS": "2",
                "ANDON_CORD_PULLED": "False"
            },
            description="Creates a simple greeter function"
        )
        greeter_fn_version = greeter_fn.latest_version
        greeter_fn_version_alias = _lambda.Alias(
            self,
            "greeterFnAlias",
            alias_name="MystiqueAutomation",
            version=greeter_fn_version
        )

        # Create Custom Loggroup
        greeter_fn_lg = _logs.LogGroup(
            self,
            "squareFnLoggroup",
            log_group_name=f"/aws/lambda/{greeter_fn.function_name}",
            retention=_logs.RetentionDays.ONE_WEEK,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # Add DDB Read Write Permission to the Lambda
        self.ddb_table_01.grant_read_write_data(greeter_fn)

        # Add API GW front end for the Lambda
        back_end_api_stage_01_options = _apigw.StageOptions(
            stage_name="miztiik",
            logging_level=_apigw.MethodLoggingLevel.INFO
        )

        # Create API Gateway
        uncached_api = _apigw.RestApi(
            self,
            "backEnd01Api",
            rest_api_name=f"{back_end_api_name}",
            deploy_options=back_end_api_stage_01_options,
            minimum_compression_size=0,
            endpoint_types=[
                _apigw.EndpointType.EDGE
            ],
            description=f"{GlobalArgs.OWNER}: API Best Practice Demonstration - Cached-vs-UnCached APIs"
        )

        back_end_01_api_res = uncached_api.root.add_resource(
            "uncached")
        res_movie = back_end_01_api_res.add_resource("movie")

        res_movie_method_get = res_movie.add_method(
            http_method="GET",
            request_parameters={
                "method.request.header.InvocationType": True,
                "method.request.path.number": True
            },
            integration=_apigw.LambdaIntegration(
                handler=greeter_fn,
                proxy=True
            )
        )

        # Outputs
        output_1 = core.CfnOutput(
            self,
            "UncachedApiUrl",
            value=f"{res_movie.url}",
            description="Use an utility like artitllery to generate load against this API."
        )
        output_2 = core.CfnOutput(
            self,
            "ddbDataLoaderStatus",
            value=f"{data_loader_status.response}",
            description="Waf Rate Rule Creator Status"
        )
