# AWS Lambda Function for Bedrock Integration
# Function Name: ml-discovery-test_beedrock

import json
import boto3
import os

def lambda_handler(event, context):
    """
    AWS Lambda function to invoke Bedrock models
    Expected to be deployed with function name: ml-discovery-test_beedrock
    """
    
    try:
        # Initialize Bedrock client
        bedrock_runtime = boto3.client('bedrock-runtime')
        
        # Extract parameters from event
        messages = event.get('messages', [])
        model_kwargs = event.get('model_kwargs', {})
        
        # Default model configuration
        model_id = "amazon.titan-text-express-v1"
        max_tokens = model_kwargs.get('maxTokenCount', 4096)
        temperature = model_kwargs.get('temperature', 0.1)
        top_p = model_kwargs.get('topP', 0.9)
        
        # Convert messages to prompt format
        prompt = ""
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            if role == 'user':
                prompt += f"Human: {content}\n"
            elif role == 'assistant':
                prompt += f"Assistant: {content}\n"
            else:
                prompt += f"{content}\n"
        
        prompt += "Assistant:"
        
        # Prepare request body for Titan model
        request_body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens,
                "temperature": temperature,
                "topP": top_p,
                "stopSequences": []
            }
        }
        
        # Invoke Bedrock model
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
            contentType='application/json'
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        generated_text = response_body['results'][0]['outputText']
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': {
                    'content': generated_text.strip()
                }
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'errorMessage': str(e),
                'errorType': type(e).__name__
            })
        }
