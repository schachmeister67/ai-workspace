# Lambda Version Configuration Guide

## Overview
This guide explains how to set up and use the Lambda version of the AI SQL agent (`text_to_sql_ai_agent_v2.py`) that routes Bedrock calls through AWS Lambda function "ml-discovery-test_beedrock".

## Architecture
```
Client App → text_to_sql_ai_agent_v2.py → AWS Lambda (ml-discovery-test_beedrock) → Amazon Bedrock → PostgreSQL Database
```

## Prerequisites

### 1. AWS Lambda Function Setup
Deploy the Lambda function with these specifications:
- **Function Name**: `ml-discovery-test_beedrock` (exact name required)
- **Runtime**: Python 3.9+
- **Timeout**: 30 seconds minimum
- **Memory**: 512 MB minimum

### 2. Lambda Function Code
Use the code from `lambda_bedrock_function.py` and deploy it to your Lambda function.

### 3. Lambda IAM Permissions
Your Lambda function needs these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/amazon.titan-text-express-v1"
            ]
        }
    ]
}
```

### 4. Client Application Setup
Install dependencies:
```bash
pip install -r requirements_bedrock.txt
```

Configure environment variables:
```
DATABASE_URL=postgresql://username:password@host:port/database_name
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
```

### 5. Client IAM Permissions
Your client application needs these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": [
                "arn:aws:lambda:*:*:function:ml-discovery-test_beedrock"
            ]
        }
    ]
}
```

## Usage

### Import and Use
```python
from text_to_sql_ai_agent_v2 import process_query

# Process a natural language query
result = process_query("How many customers do we have?")

print(f"SQL: {result['sql_query']}")
print(f"Result: {result['result']}")
print(f"Raw Data: {result['json_result']}")
```

### Running the Test
```bash
python text_to_sql_ai_agent_v2.py
```

## Key Features

### 1. Lambda Integration
- **Custom Chat Model**: `LambdaBedrockChat` class that implements LangChain's `BaseChatModel`
- **Structured Output Support**: Custom wrapper for handling Pydantic models
- **Error Handling**: Graceful fallback on Lambda errors
- **Message Format**: Automatic conversion between LangChain and Lambda message formats

### 2. Preserved Functionality
- **All original methods intact**: `query_gen`, `query_check`, `query_execute`, `process_query`
- **Same API**: Drop-in replacement for the original agent
- **All system prompts preserved**: Identical SQL generation behavior
- **JSON result capture**: Raw database results still available

### 3. Lambda Function Features
- **Titan Text Express**: Cost-effective model for SQL generation
- **Configurable parameters**: Temperature, max tokens, top-p
- **Error handling**: Proper error responses for debugging
- **JSON format**: Standard input/output format

## Benefits of Lambda Architecture

### 1. **Scalability**
- Automatic scaling based on demand
- No cold start issues for database operations
- Concurrent execution support

### 2. **Security**
- Lambda function isolated from client environment
- Bedrock credentials stay in Lambda
- VPC support for database access

### 3. **Cost Optimization**
- Pay-per-request Lambda pricing
- No idle time costs
- Shared Lambda function across multiple clients

### 4. **Centralized Management**
- Single Lambda function for multiple applications
- Centralized model configuration
- Easier monitoring and logging

## Deployment Steps

### 1. Deploy Lambda Function
```bash
# Create deployment package
zip -r lambda-deployment.zip lambda_bedrock_function.py

# Deploy via AWS CLI
aws lambda create-function \
    --function-name ml-discovery-test_beedrock \
    --runtime python3.9 \
    --role arn:aws:iam::ACCOUNT:role/lambda-execution-role \
    --handler lambda_bedrock_function.lambda_handler \
    --zip-file fileb://lambda-deployment.zip \
    --timeout 30 \
    --memory-size 512
```

### 2. Configure Lambda Environment
Set environment variables in Lambda if needed:
- `AWS_DEFAULT_REGION`: Region for Bedrock access

### 3. Test Lambda Function
```bash
aws lambda invoke \
    --function-name ml-discovery-test_beedrock \
    --payload '{"messages":[{"role":"user","content":"SELECT 1"}],"model_kwargs":{"maxTokenCount":100}}' \
    response.json
```

### 4. Deploy Client Application
Use `text_to_sql_ai_agent_v2.py` in your application with proper AWS credentials.

## Monitoring and Debugging

### 1. CloudWatch Logs
- Lambda function logs in CloudWatch
- Error messages and execution details
- Performance metrics

### 2. Lambda Metrics
- Invocation count
- Duration
- Error rate
- Throttles

### 3. Client-side Debugging
- Error messages returned in response
- Lambda invocation status
- Network connectivity issues

## Troubleshooting

### Common Issues

1. **Lambda function not found**:
   - Verify function name is exactly `ml-discovery-test_beedrock`
   - Check AWS region consistency
   - Verify IAM permissions

2. **Bedrock access denied in Lambda**:
   - Check Lambda execution role permissions
   - Verify Bedrock model is enabled in the region
   - Check model ID spelling

3. **Timeout errors**:
   - Increase Lambda timeout (max 15 minutes)
   - Check Bedrock model response time
   - Verify network connectivity

4. **High costs**:
   - Monitor Lambda invocations
   - Check Bedrock token usage
   - Optimize prompt length

## Performance Optimization

### 1. Lambda Optimization
- Use provisioned concurrency for consistent performance
- Optimize memory allocation
- Monitor cold start times

### 2. Bedrock Optimization
- Use shorter prompts when possible
- Set appropriate token limits
- Monitor model response times

### 3. Database Optimization
- Use connection pooling
- Optimize SQL queries
- Monitor database performance

## Security Best Practices

### 1. Lambda Security
- Use least privilege IAM roles
- Enable encryption at rest and in transit
- Regular security updates

### 2. Network Security
- Use VPC for database access
- Implement proper security groups
- Monitor network traffic

### 3. Data Protection
- Encrypt sensitive data
- Implement proper logging
- Regular security audits
