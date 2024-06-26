# -*- coding: utf-8 -*-
"""HealthmateBot_datacollection.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1e5X64YcsfTL-ZvS9ZYtNHevUZvufbnle

# HealthmateBot-Datbase Creation

We aimed to create a database for our Healthmate bot within the sensitive healthcare domain, where data provided to the user must be accurate and trustworthy. However, sourcing open-source data posed a challenge due to its sensitive nature. Our bot's primary objective was to provide related diagnoses based on user-provided symptoms, yet acquiring a complete dataset of symptoms and associated conditions proved elusive. Consequently, we shifted focus to offering summaries and relevant physician specialties, along with nearby hospitals specializing in those areas, leveraging available resources. The latest XML data was imported from https://medlineplus.gov/xml.html, and the code below demonstrates the conversion of the XML file into a CSV format.

To gather information on various conditions and their summaries, the latest XML data is imported from https://medlineplus.gov/xml.html. The code provided below facilitates the conversion of the XML file into a CSV format. This resulting file contains essential details such as the Condition, Also Called, and Full Summary.
"""

import csv
import json

# Read data from the CSV file with 'latin-1' encoding
with open('Book1.csv', mode='r', encoding='latin-1') as file:
    csv_reader = csv.DictReader(file)
    data = [row for row in csv_reader]

# Extract 'tag' and 'responses' fields
tag_responses_data = []
for row in data:
    tag = row['tag']
    responses = json.loads(row['responses'])
    for response in responses:
        tag_responses_data.append([tag, response.strip()])

# Save the data to a new CSV file
with open('tag_responses_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Tag', 'Responses'])  # Writing the header
    writer.writerows(tag_responses_data)  # Writing the data rows

print("Data saved successfully as tag_responses_data.csv")

"""The summary section was lengthy, and we condensed it into a shorter, more concise form as given below."""

import pandas as pd
import spacy

# Load the English tokenizer, tagger, parser, NER, and word vectors
nlp = spacy.load("en_core_web_sm")

# Read the CSV file
df = pd.read_csv('health_topics.csv')

# Access the 'Full Summary' column
summaries = df['Full Summary']

# Initialize a list to store the condensed summaries
condensed_summaries = []

# Loop through the summaries and apply NLP processing
for summary in summaries:
    doc = nlp(summary)

    # Extract the most relevant sentences, e.g., the first two sentences
    condensed_summary = ' '.join([sent.text for sent in doc.sents][:2])

    # Append the condensed summary to the list
    condensed_summaries.append(condensed_summary)

# Add the condensed summaries to the DataFrame
df['Condensed Summary'] = condensed_summaries

# Save the DataFrame to a new CSV file
df.to_csv('health_topics_condensed.csv', index=False)

"""However, this data lacks relevant physician department information such as Endocrinology for diabetes. To address this gap, we utilized web scraping to extract the body part associated with each medical condition using the code provided below. This process generates data containing the condition and its relevant body part associations. Subsequently, based on these body part associations, we tagged the relevant physician departments."""

import requests
from bs4 import BeautifulSoup
import csv

# Function to scrape and extract data
def scrape_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    bodypart_element = soup.find('div', class_='page-info')
    content_elements = soup.find_all('li', class_='item')

    if bodypart_element:
        bodypart = bodypart_element.get_text(strip=True)

    if content_elements:
        data = []
        for content_element in content_elements:
            content = content_element.get_text(strip=True)
            data.append([content, bodypart])

        # Write to CSV
        with open('output.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(data)

        print(f"Data from {url} written to output.csv successfully.")

# List of URLs to scrape
urls = ['https://medlineplus.gov/bloodheartandcirculation.html',
        'https://medlineplus.gov/bonesjointsandmuscles.html',
        'https://medlineplus.gov/brainandnerves.html',
        'https://medlineplus.gov/digestivesystem.html',
        'https://medlineplus.gov/earnoseandthroat.html',
        'https://medlineplus.gov/endocrinesystem.html',
        'https://medlineplus.gov/eyesandvision.html',
        'https://medlineplus.gov/immunesystem.html',
        'https://medlineplus.gov/kidneysandurinarysystem.html',
        'https://medlineplus.gov/lungsandbreathing.html',
        'https://medlineplus.gov/mouthandteeth.html',
        'https://medlineplus.gov/skinhairandnails.html',
        'https://medlineplus.gov/femalereproductivesystem.html',
        'https://medlineplus.gov/malereproductivesystem.html',
        'https://medlineplus.gov/cancers.html',
        'https://medlineplus.gov/diabetesmellitus.html',
        'https://medlineplus.gov/geneticsbirthdefects.html',
        'https://medlineplus.gov/infections.html',
        'https://medlineplus.gov/mentalhealthandbehavior.html',
        'https://medlineplus.gov/metabolicproblems.html',
        'https://medlineplus.gov/injuriesandwounds.html',
        'https://medlineplus.gov/poisoningtoxicologyenvironmentalhealth.html',
        'https://medlineplus.gov/pregnancyandreproduction.html',
        'https://medlineplus.gov/substanceabuseproblems.html',
        'https://medlineplus.gov/complementaryandalternativetherapies.html',
        'https://medlineplus.gov/diagnostictests.html',
        'https://medlineplus.gov/drugtherapy.html',
        'https://medlineplus.gov/surgeryandrehabilitation.html',
        'https://medlineplus.gov/symptoms.html',
        'https://medlineplus.gov/transplantationanddonation.html',
        'https://medlineplus.gov/childrenandteenagers.html',
        'https://medlineplus.gov/men.html',
        'https://medlineplus.gov/olderadults.html',
        'https://medlineplus.gov/populationgroups.html',
        'https://medlineplus.gov/women.html']

# Loop through the URLs and scrape data
for url in urls:
    scrape_data(url)

"""We utilized CMS data from Maryland to acquire information regarding nearby hospitals with those medical specialists. The dataset can be accessed at https://data.cms.gov/provider-data/dataset/mj5m-pzi6."""

