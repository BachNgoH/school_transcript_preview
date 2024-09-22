import streamlit as st
import json
from PIL import Image
import os
from pdf2image import convert_from_path
import pandas as pd

# Function to load JSON data
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Function to convert PDF to images
def pdf_to_images(pdf_path):
    return convert_from_path(pdf_path)

# Load JSON data
hocba1_data = load_json('./data/hocba_1_result_full.json')
hocba2_data = load_json('./data/hocba_2_result_full.json')
hocba3_data = load_json('./data/hocba_3_result_full.json')

st.title('Document Classifier Results')

# Create tabs for each document
tab1, tab2, tab3 = st.tabs(["hocba1", "hocba2", "hocba3"])

for idx, (tab, pdf_file, json_data) in enumerate(zip([tab1, tab2, tab3], 
                                                     ['./resources/hocba_test1.pdf', './resources/hocba_test2.pdf', './resources/hocba_test3.pdf'],
                                                     [hocba1_data, hocba2_data, hocba3_data]), start=1):
    with tab:
        # st.header(f"{pdf_file}")
        print(f"Processing {pdf_file}")
        
        # Convert PDF to images if not already done
        images_folder = f"./resources/hocba{idx}_images"
        if not os.path.exists(images_folder):
            os.makedirs(images_folder)
            images = pdf_to_images(pdf_file)
            print(images)
            for i, image in enumerate(images):
                image.save(f"{images_folder}/page_{i+1}.jpg", "JPEG")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Page navigation
            max_pages = len(os.listdir(images_folder))
            page_number = st.number_input(f"Page number for {pdf_file}", min_value=1, max_value=max_pages, value=1, key=f"page_{idx}")
            
            # Display PDF page image
            image_path = f"{images_folder}/page_{page_number}.jpg"
            image = Image.open(image_path)
            st.image(image, caption=f"Page {page_number}", use_column_width=True)
        
        with col2:
            # Display parsing results
            st.subheader("Parsing Results")
            page_data = next((page for page in json_data['pages'] if page['page_number'] == page_number), None)
            if page_data and page_data.get('sections'):
                section = page_data['sections'][0]  # Assuming there's only one section per page
                st.subheader(f"Grade: {section.get('grade', 'N/A')}")
                
                subjects = section.get('subjects', [])
                if subjects:
                    # Create a DataFrame for the subjects
                    df = pd.DataFrame(subjects)
                    df = df.set_index('name')
                    df = df.rename(columns={
                        'gpa_term_1': 'Term 1',
                        'gpa_term_2': 'Term 2',
                        'gpa_cn': 'Final'
                    })
                    
                    # Round all numeric columns to one decimal place
                    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
                    df[numeric_columns] = df[numeric_columns].round(1)
                    
                    # Display the table
                    st.table(df)
                else:
                    st.write("No subject data available for this page.")
            else:
                st.write("No data available for this page.")

st.sidebar.title("About")
st.sidebar.info("This Streamlit app displays the results of the document classifier for hocba1.pdf, hocba2.pdf, and hocba3.pdf.")
