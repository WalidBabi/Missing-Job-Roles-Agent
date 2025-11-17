# Frontend Deployment Script - PowerShell
# Deploys React frontend to S3 and CloudFront

$PROJECT_NAME = "missing-roles-agent"
$ENVIRONMENT = if ($env:ENVIRONMENT) { $env:ENVIRONMENT } else { "production" }
$AWS_REGION = if ($env:AWS_REGION) { $env:AWS_REGION } else { "us-east-1" }

Write-Host "Deploying Frontend to AWS" -ForegroundColor Green

# Get S3 bucket name from CloudFormation
$STACK_NAME = "${PROJECT_NAME}-${ENVIRONMENT}-infrastructure"
$BUCKET_NAME = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" --output text)
$ALB_ENDPOINT = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='ALBEndpoint'].OutputValue" --output text)

Write-Host "S3 Bucket: ${BUCKET_NAME}" -ForegroundColor Yellow
Write-Host "API Endpoint: http://${ALB_ENDPOINT}" -ForegroundColor Yellow

# Build frontend
Write-Host "`n[1/3] Building frontend..." -ForegroundColor Green
Set-Location frontend
npm install
$env:VITE_API_URL = "http://${ALB_ENDPOINT}/api"
npm run build

# Upload to S3
Write-Host "`n[2/3] Uploading to S3..." -ForegroundColor Green
aws s3 sync dist/ "s3://${BUCKET_NAME}/" --delete --region "${AWS_REGION}"

# Invalidate CloudFront cache
Write-Host "`n[3/3] Invalidating CloudFront cache..." -ForegroundColor Green
$DISTRIBUTION_ID = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" --output text)

if ($DISTRIBUTION_ID) {
    aws cloudfront create-invalidation --distribution-id "${DISTRIBUTION_ID}" --paths "/*" --region "${AWS_REGION}"
    Write-Host "CloudFront cache invalidated" -ForegroundColor Green
} else {
    Write-Host "CloudFront distribution ID not found. Skipping cache invalidation." -ForegroundColor Yellow
}

$CLOUDFRONT_URL = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='CloudFrontURL'].OutputValue" --output text)

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Frontend Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Frontend URL: https://${CLOUDFRONT_URL}"
Write-Host "S3 Bucket: ${BUCKET_NAME}"

Set-Location ..

