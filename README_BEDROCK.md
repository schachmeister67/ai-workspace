# AWS Bedrock Configuration Guide

## Overview
This guide explains how to set up and use the AWS Bedrock version of the AI SQL agent (`text_to_sql_ai_agent.py`).

## Prerequisites

### 1. AWS Account Setup
- AWS account with Bedrock access enabled
- Bedrock models must be enabled in your AWS region
- Proper IAM permissions for Bedrock usage

### 2. Install Dependencies
```bash
pip install -r requirements_bedrock.txt
```

### 3. AWS Configuration
Set up your AWS credentials using one of these methods:

#### Option A: Environment Variables (.env file)
```
DATABASE_URL=postgresql://username:password@host:port/database_name
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
```

#### Option B: AWS CLI Configuration
```bash
aws configure
```

#### Option C: IAM Roles (for EC2/Lambda deployment)
Use IAM roles attached to your compute resources.

## Model Selection

The agent uses **Amazon Titan Text Express** (`amazon.titan-text-express-v1`) as the default model because:
- **Cost-efficient**: Lower cost per token compared to other models
- **Fast inference**: Quick response times for SQL generation
- **Good accuracy**: Reliable for text-to-SQL tasks
- **Wide availability**: Available in most AWS regions

### Alternative Models
You can modify the model in `text_to_sql_ai_agent.py` by changing the `model_id`:

```python
llm = ChatBedrock(
    client=bedrock_runtime,
    model_id="amazon.titan-text-express-v1",  # Change this line
    model_kwargs={...}
)
```

**Other cost-effective options:**
- `amazon.titan-text-lite-v1` - Even more cost-effective but less capable
- `anthropic.claude-3-haiku-20240307-v1:0` - Good balance of cost and performance
- `cohere.command-text-v14` - Alternative cost-effective option

## Required AWS Permissions

Your AWS user/role needs these permissions:
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

## Usage

### Import and Use
```python
from text_to_sql_ai_agent import process_query

# Process a natural language query
result = process_query("How many customers do we have?")

print(f"SQL: {result['sql_query']}")
print(f"Result: {result['result']}")
print(f"Raw Data: {result['json_result']}")
```

### Running the Test
```bash
python text_to_sql_ai_agent.py
```

## Cost Optimization Tips

1. **Use Titan Text Express**: Most cost-effective for SQL generation
2. **Set appropriate token limits**: Configure `maxTokenCount` based on your needs
3. **Use low temperature**: Set temperature to 0.1 for more deterministic results
4. **Monitor usage**: Use AWS CloudWatch to track Bedrock usage and costs
5. **Regional selection**: Choose regions with lower Bedrock pricing

## Troubleshooting

### Common Issues

1. **Model not available error**:
   - Enable the model in AWS Bedrock console
   - Check if the model is available in your region

2. **Permission denied**:
   - Verify IAM permissions
   - Check AWS credentials configuration

3. **Import errors**:
   - Install required dependencies: `pip install -r requirements_bedrock.txt`
   - Ensure `langchain-aws` is properly installed

4. **High costs**:
   - Switch to `amazon.titan-text-lite-v1` for even lower costs
   - Reduce `maxTokenCount` in model configuration
   - Monitor and set up billing alerts

## Performance Comparison

| Model | Cost (relative) | Speed | SQL Accuracy |
|-------|----------------|-------|--------------|
| Titan Text Express | Low | Fast | Good |
| Titan Text Lite | Very Low | Very Fast | Fair |
| Claude 3 Haiku | Medium | Fast | Excellent |
| Claude 3 Sonnet | High | Medium | Excellent |

## Support

For AWS Bedrock specific issues:
1. Check AWS Bedrock documentation
2. Verify model availability in your region
3. Review CloudWatch logs for detailed error messages
4. Contact AWS support for Bedrock-related problems
