
import os  
import base64
from openai import AzureOpenAI  

endpoint = os.getenv("ENDPOINT_URL", "https://gongz-m82drk07-eastus2.openai.azure.com/")  
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o-2024-08-06-ft-c1933f4a82bd4d5f8132bb22e643a204-2")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "")  

# Initialize Azure OpenAI Service client with key-based authentication    
client = AzureOpenAI(  
    azure_endpoint=endpoint,  
    api_key=subscription_key,  
    api_version="2024-05-01-preview",
)
    
    
# IMAGE_PATH = "YOUR_IMAGE_PATH"
# encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')

#Prepare the chat prompt 
chat_prompt = [
    {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": "You are an AI agent expert in writing unit tests. "
        "Your task is to write unit tests for the given code files of the repository. "
        "Make sure the tests can be executed without lint or compile errors."
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": ""
            }
        ]
    },
] 
    
# Include speech result if speech is enabled  
messages = chat_prompt  
    
# Generate the completion  
completion = client.chat.completions.create(  
    model=deployment,
    messages=messages,
    max_tokens=16000,  
    temperature=0.7,  
    top_p=0.95,  
    frequency_penalty=0,  
    presence_penalty=0,
    stop=None,  
    stream=False
)

print(completion.to_json())  
    