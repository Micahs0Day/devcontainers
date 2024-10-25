from cdktf import App, TerraformStack
from constructs import Construct
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws import data_aws_iam_policy_document, s3_bucket, s3_bucket_policy, cloudtrail
from constructs import Construct
from cdktf import Token, TerraformStack
import os

suffix = '0001'
account_id = os.environ.get('AWS_ACCOUNT_ID')
mngmt_events = os.environ.get('CLOUDTRAIL_MNG_EVENTS')
rw_type = os.environ.get('CLOUDTRAIL_RW_TYPE')

if mngmt_events == "False":
    mngmt_events = False
else:
    mngmt_events = True

class MyStack_Deploy(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # AWS Provider
        AwsProvider(self, "AWS", region="us-east-1")

        # S3 Bucket for CloudTrail logs
        log_bucket = s3_bucket.S3Bucket(self, "CloudTrailBucket",
            bucket=f"m0d-test-{suffix}",
            force_destroy= True
        )

        # S3 Bucket Policy to allow CloudTrail to write logs
        allow_trail_access = data_aws_iam_policy_document.DataAwsIamPolicyDocument(self, "allow_trail_access",
            statement=[data_aws_iam_policy_document.DataAwsIamPolicyDocumentStatement(
                actions=["s3:GetBucketAcl"],
                effect="Allow",
                principals=[data_aws_iam_policy_document.DataAwsIamPolicyDocumentStatementPrincipals(
                    identifiers=["cloudtrail.amazonaws.com"],
                    type="Service"
                )
                ],
                resources=[f"arn:aws:s3:::{log_bucket.bucket}"],
                condition=[data_aws_iam_policy_document.DataAwsIamPolicyDocumentStatementCondition(
                    test="StringEquals",
                    values=[f"arn:aws:cloudtrail:us-east-1:{account_id}:trail/m0d-cloudtrail-trail-{suffix}"],
                    variable="aws:SourceArn"
                )]
            ),
            data_aws_iam_policy_document.DataAwsIamPolicyDocumentStatement(
                actions=["s3:PutObject"],
                effect="Allow",
                principals=[data_aws_iam_policy_document.DataAwsIamPolicyDocumentStatementPrincipals(
                    identifiers=["cloudtrail.amazonaws.com"],
                    type="Service"
                )
                ],
                resources=[f"arn:aws:s3:::{log_bucket.bucket}/AWSLogs/{account_id}/*"],
                condition=[data_aws_iam_policy_document.DataAwsIamPolicyDocumentStatementCondition(
                    test="StringEquals",
                    values=["bucket-owner-full-control"],
                    variable="s3:x-amz-acl"
                ),
                data_aws_iam_policy_document.DataAwsIamPolicyDocumentStatementCondition(
                    test="StringEquals",
                    values=[f"arn:aws:cloudtrail:us-east-1:{account_id}:trail/m0d-cloudtrail-trail-{suffix}"],
                    variable="aws:SourceArn")
                ]
            )
            ]
        )

        aws_s3_bucket_policy = s3_bucket_policy.S3BucketPolicy(self, "allow_trail_access_policy",
            bucket=log_bucket.bucket,
            policy=Token.as_string(allow_trail_access.json)
        )

         # CloudTrail Trail
        trail = cloudtrail.Cloudtrail(self, "trail-test",
            name=f"m0d-cloudtrail-trail-{suffix}",
            s3_bucket_name=log_bucket.bucket,
            depends_on=[aws_s3_bucket_policy],
            event_selector=[cloudtrail.CloudtrailEventSelector(
                data_resource=[cloudtrail.CloudtrailEventSelectorDataResource(
                    type="AWS::S3::Object",
                    values=["arn:aws:s3"]
                )
                ],
                include_management_events=mngmt_events,
                read_write_type=rw_type
            )
            ]
        )

app = App()
MyStack_Deploy(app, "cloudtrail-create-stack")
app.synth()
