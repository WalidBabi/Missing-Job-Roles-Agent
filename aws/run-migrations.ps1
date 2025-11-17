# Run Django Migrations on ECS - PowerShell Script

$PROJECT_NAME = "missing-roles-agent"
$ENVIRONMENT = if ($env:ENVIRONMENT) { $env:ENVIRONMENT } else { "production" }
$AWS_REGION = if ($env:AWS_REGION) { $env:AWS_REGION } else { "us-east-1" }

$STACK_NAME = "${PROJECT_NAME}-${ENVIRONMENT}-infrastructure"
$CLUSTER_NAME = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='ECSClusterName'].OutputValue" --output text)
$TASK_DEFINITION = "${PROJECT_NAME}-backend"

$VPC_ID = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='VPCId'].OutputValue" --output text)
$PRIVATE_SUBNETS = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='PrivateSubnetIds'].OutputValue" --output text)
$PRIVATE_SUBNET_1 = $PRIVATE_SUBNETS.Split(',')[0]

$ECS_SG = (aws ec2 describe-security-groups --filters "Name=vpc-id,Values=${VPC_ID}" "Name=group-name,Values=${PROJECT_NAME}-${ENVIRONMENT}-ecs-sg" --region "${AWS_REGION}" --query "SecurityGroups[0].GroupId" --output text)

Write-Host "Running migrations on cluster: ${CLUSTER_NAME}"

aws ecs run-task `
    --cluster "${CLUSTER_NAME}" `
    --task-definition "${TASK_DEFINITION}" `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[${PRIVATE_SUBNET_1}],securityGroups=[${ECS_SG}],assignPublicIp=DISABLED}" `
    --overrides "{`"containerOverrides`":[{`"name`":`"backend`",`"command`":[`"python`",`"manage.py`",`"migrate`"]}]}" `
    --region "${AWS_REGION}"

Write-Host "Migration task started. Check ECS console for status."

