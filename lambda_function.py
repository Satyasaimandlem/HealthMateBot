import openai
import boto3
import pandas as pd
from io import StringIO
import re

# Configure OpenAI API key
api_key = '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'
openai.api_key = api_key


# Function to get a concise statement about the medical specialty for a health condition
def get_specialty_for_condition(health_condition):
    prompt = f"What is the medical specialty for treating {health_condition}?"
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"


# Function to invoke OpenAI API for health condition summary
def get_health_condition_summary(health_condition):
    prompt = f"Can you provide a summary for the health condition: {health_condition}?"
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"


def fetch_data_from_s3(bucket_name, file_keys):
    s3 = boto3.client('s3')
    data = {}
    for key in file_keys:
        obj = s3.get_object(Bucket=bucket_name, Key=key)
        data[key] = pd.read_csv(obj['Body'])
    return data


def get_physician_for_condition(data, health_condition):
    physician_df = data['FINAL_DATA.csv']

    # Print the DataFrame to verify its contents
    print(physician_df)

    try:
        # Filter the DataFrame based on the health condition
        condition_matches = physician_df['Health Condition'].str.lower() == health_condition.lower()
        filtered_physicians = physician_df[condition_matches]
        # Print the filtered DataFrame for inspection
        print(filtered_physicians)

        if not filtered_physicians.empty:
            # Get the first physician if there are matching rows
            physician = filtered_physicians['Physician'].iloc[0]
            return physician
        else:
            # Handle the case when no matching rows are found
            return "No physician found for the given health condition."
    except Exception as e:
        return f"Error: {str(e)}"


def find_top_five_hospitals(data, physician, zipcode):
    hospitals_df = data['Providers_DATA_MD (1).csv']

    try:
        if pd.isnull(physician) or physician == "":
            return {
                "fulfillmentText": "No physician found for the given health condition."
            }

        relevant_hospitals = hospitals_df[hospitals_df['Physician'].str.contains(physician, case=False, na=False)]
        hospitals_in_zipcode = relevant_hospitals[relevant_hospitals['ZIP Code'] == int(zipcode)]

        top_five_hospitals = hospitals_in_zipcode.head(5)

        # Return the DataFrame
        return top_five_hospitals

    except Exception as e:
        return {
            "fulfillmentText": f"Error: {str(e)}"
        }

def location(parameters):
    loc = int(parameters["zip-code"])
    title = parameters["synonymsdatafile"]
    title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    title = title.lower()

    try:
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket='dilogflowchatbot', Key='Providers_DATA_MD (1).csv')
        data = response['Body'].read().decode('utf-8')
        df_providers = pd.read_csv(StringIO(data))

        # Print loc to verify its format
        print(f"ZIP Code received: {loc}")

        # Print DataFrame info for troubleshooting
        print(df_providers.info())

        # Check if there are any rows where 'ZIP Code' matches the provided loc
        filtered_hospitals = df_providers[df_providers['ZIP Code'] == loc]

        # Print the filtered data to inspect
        print(filtered_hospitals)

        if not filtered_hospitals.empty:
            result_paragraph = "\n".join([
                f"{idx + 1}.\n   First Name: {row['frst_nm']}\n   Last Name: {row['lst_nm']}\n   Physician: {row['Physician']}\n   Address: {row['adr_ln_1']}\n   City/Town: {row['City/Town']}\n   State: {row['State']}\n   Zip Code: {row['ZIP Code']}\n"
                for idx, row in filtered_hospitals.iterrows()
            ])
            return {
                "fulfillmentText": f"{result_paragraph}"
            }
        else:
            return {
                "fulfillmentText": "No hospitals found for the given ZIP Code."
            }
    except Exception as e:
        return {
            "fulfillmentText": f"Error: {str(e)}"
        }


def lambda_handler(event, context):
    intent_name = event.get('queryResult', {}).get('intent', {}).get('displayName')

    if intent_name == 'SummaryOfHealthCondition':
        health_condition = event.get('queryResult', {}).get('parameters', {}).get('HealthCondition')
        summary = get_health_condition_summary(health_condition)
        return {
            "fulfillmentText": f"Health Condition Summary: {summary}"
        }

    elif intent_name == 'ProvidePhysician':
        health_condition = event.get('queryResult', {}).get('parameters', {}).get('HealthCondition')
        specialty = get_specialty_for_condition(health_condition)
        return {
            "fulfillmentText": f"Specialty: {specialty}"
        }


    elif intent_name == 'NearbyHospitals':
        health_condition = event.get('queryResult', {}).get('parameters', {}).get('HealthCondition')
        zipcode = event.get('queryResult', {}).get('parameters', {}).get('ZipCode')

        s3_data = fetch_data_from_s3('dilogflowchatbot', ['Providers_DATA_MD (1).csv', 'FINAL_DATA.csv'])
        physician = get_physician_for_condition(s3_data, health_condition)
        top_five_hospitals = find_top_five_hospitals(s3_data, physician, zipcode)

        response_text = ""
        for idx, hospital in top_five_hospitals.head(5).iterrows():
            response_text += f"First Name: {hospital['frst_nm']} Last Name: {hospital['lst_nm']} Physician: {hospital['Physician']} Address: {hospital['adr_ln_1']} City: {hospital['City/Town']} State: {hospital['State']} ZIP Code: {hospital['ZIP Code']} -----------------------------\n"

        return {
            "fulfillmentText": response_text
        }
    
    return {
        "fulfillmentText": "Intent not recognized."
    }

