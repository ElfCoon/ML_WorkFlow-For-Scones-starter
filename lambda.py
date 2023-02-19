#Lambda Function 1

import json
import boto3
import base64

# A low-level client representing Amazon Simple Storage Service (S3)
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input 
    key = event['s3_key']                              
    bucket = event['s3_bucket']                        
    
    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, "/tmp/image.png")
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:         
        image_data = base64.b64encode(f.read())      

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    
   
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,      
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }



#Lambda Function 2 - Image Classifier

import json
import base64
import boto3

# Using low-level client representing Amazon SageMaker Runtime 
runtime_client = boto3.client('sagemaker-runtime')                   


# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2023-02-19-06-03-57-634" 


def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['image_data'])     

    # Instantiate a Predictor (Here we have renamed 'Predictor' to 'response')
    # Response after invoking a deployed endpoint via SageMaker Runtime 
    response = runtime_client.invoke_endpoint(
                                        EndpointName=ENDPOINT,   
                                        Body=image,               
                                        ContentType='image/png'   
                                    )
                                    
    
    # Make a prediction: Unpack reponse
    
    inferences = json.loads(response['Body'].read().decode('utf-8'))     
  
    
    # We return the data back to the Step Function    
    event['inferences'] = inferences                          
    return {
        'statusCode': 200,
        'body': event                         
    }


#Lambda Function 3  - Low Confidence Inference

import json

THRESHOLD = 0.70


def lambda_handler(event, context):
    
    # Grab the inferences from the event## TODO: fill in
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(list(inferences))>THRESHOLD   
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise Exception("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': event       
    }