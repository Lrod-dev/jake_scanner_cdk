from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_codebuild as codebuild,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    Duration,
    RemovalPolicy,
)
from constructs import Construct
import os

class JakeScannerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        input_bucket = s3.Bucket(self, "InputBucket",
            bucket_name="env-scan-input",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        output_bucket = s3.Bucket(self, "OutputBucket",
            bucket_name="env-scan-results",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        lambda_role = iam.Role(self, "JakeLambdaExecutionRole",
            role_name="JakeScanPipeline-LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        lambda_role.add_to_policy(iam.PolicyStatement(
            actions=["codebuild:StartBuild"],
            resources=["*"]
        ))

        lambda_fn = _lambda.Function(self, "S3TriggerLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(30),
            environment={
                "CODEBUILD_PROJECT_NAME": "JakeScanBuild"
            },
            role=lambda_role
        )

        event_rule = events.Rule(self, "S3UploadRule",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={
                    "bucket": {"name": [input_bucket.bucket_name]},
                    "object": {"key": [{"suffix": "requirements.txt"}]}
                }
            )
        )
        event_rule.add_target(targets.LambdaFunction(lambda_fn))

        codebuild_role = iam.Role(self, "JakeCodeBuildServiceRole",
            role_name="JakeScanPipeline-CodeBuildServiceRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com")
        )

        input_bucket.grant_read(codebuild_role)
        output_bucket.grant_write(codebuild_role)

        codebuild_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "s3:GetObject", "s3:PutObject",
                "logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"
            ],
            resources=["*"]
        ))

        codebuild.Project(self, "JakeScanBuild",
            project_name="JakeScanBuild",
            role=codebuild_role,
            source=codebuild.Source.asset("."),
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables={
                    "S3_KEY": codebuild.BuildEnvironmentVariable(value=""),
                    "BUCKET_NAME": codebuild.BuildEnvironmentVariable(value="")
                }
            )
        )
