from cdktf import App, TerraformStack
from constructs import Construct
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws import data_aws_iam_policy_document
from cdktf_cdktf_provider_aws import s3_bucket
from cdktf_cdktf_provider_aws import s3_bucket_policy
from cdktf_cdktf_provider_aws import cloudtrail
from constructs import Construct
from cdktf import Token, TerraformStack
import string
import random
import os

account_id = os.environ.get('AWS_ACCOUNT_ID')
suffix = ''.join(random.choices(string.ascii_letters,k=5)) # initializing size of string
suffix = suffix.lower()

class MyStack_Deploy(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # AWS Provider
        AwsProvider(self, "AWS", region="us-east-1")

        # S3 Bucket for CloudTrail logs
        log_bucket = s3_bucket.S3Bucket(self, "CloudTrailBucket",
            bucket=f"m0d-test-{suffix}"
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
        trail = cloudtrail.Cloudtrail(self, "M0dCloudTrail-Test",
            name=f"m0d-cloudtrail-trail-{suffix}",
            s3_bucket_name=log_bucket.bucket,
            depends_on=[aws_s3_bucket_policy],
            event_selector=[cloudtrail.CloudtrailEventSelector(
                include_management_events=True,
                read_write_type="All"
            )
            ]
        )



class MyStack_Modify(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # AWS Provider
        AwsProvider(self, "AWS", region="us-east-1")

         # CloudTrail Trail
        trail = cloudtrail.Cloudtrail(self, "M0dCloudTrail-Test-update",
            name=f"m0d-cloudtrail-trail-{suffix}",
            s3_bucket_name=f"m0d-test-{suffix}",
            event_selector=[cloudtrail.CloudtrailEventSelector(
                include_management_events=False,
                read_write_type="ReadOnly"
            )
            ]
        )


app = App()
MyStack_Modify(app, "cloudtrail-modify-stack")
app.synth()
MyStack_Deploy(app, "cloudtrail-create-stack")
app.synth()



