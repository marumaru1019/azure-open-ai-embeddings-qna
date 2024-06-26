import streamlit as st
import os, json, re, io
from os import path
import base64
import requests
import mimetypes
import traceback
import chardet
from utilities.helper import LLMHelper
import uuid
from redis.exceptions import ResponseError 
from urllib import parse
import string
import random

def upload_text_and_embeddings():
    file_name = f"{uuid.uuid4()}.txt"
    source_url = llm_helper.blob_client.upload_file(st.session_state['doc_text'], file_name=file_name, content_type='text/plain; charset=utf-8')
    llm_helper.add_embeddings_lc(source_url) 
    st.success("Embeddings added successfully.")

def remote_convert_files_and_add_embeddings(process_all=False):
    url = os.getenv('CONVERT_ADD_EMBEDDINGS_URL')
    if process_all:
        url = f"{url}?process_all=true"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            st.success(f"{response.text}\nPlease note this is an asynchronous process and may take a few minutes to complete.")
        else:
            st.error(f"Error: {response.text}")
    except Exception as e:
        st.error(traceback.format_exc())

def delete_row():
    st.session_state['data_to_drop'] 
    redisembeddings.delete_document(st.session_state['data_to_drop'])

def add_urls():
    urls = st.session_state['urls'].split('\n')
    for url in urls:
        if url:
            llm_helper.add_embeddings_lc(url)
            st.success(f"Embeddings added successfully for {url}")

def upload_file(bytes_data: bytes, file_name: str):
    # Upload a new file
    st.session_state['filename'] = file_name
    content_type = mimetypes.MimeTypes().guess_type(file_name)[0]
    charset = f"; charset={chardet.detect(bytes_data)['encoding']}" if content_type == 'text/plain' else ''
    st.session_state['file_url'], st.session_state['file_url_witout_sas'] = llm_helper.blob_client.upload_file_without_sas(bytes_data, st.session_state['filename'], content_type=content_type+charset)

# fitz を使ってしおり分割するにはローカルにファイルがある必要がある
def download_pdf(url):
    response = requests.get(url)
    if response.status_code == 200:
        # PDFファイルの内容を一時ファイルに保存
        temp_pdf_path = "temp_downloaded.pdf"
        with open(temp_pdf_path, "wb") as f:
            f.write(response.content)
        return temp_pdf_path
    else:
        raise Exception(f"Failed to download PDF: Status code {response.status_code}")
    
def generate_random_string():
    # Characters allowed in the middle of the string
    middle_chars = string.ascii_lowercase + string.digits + '-'
    
    # Characters allowed at the ends of the string
    end_chars = string.ascii_lowercase + string.digits

    # Generate a random string of length 16
    return random.choice(end_chars) + ''.join(random.choice(middle_chars) for _ in range(14)) + random.choice(end_chars)

try:
    # Set page layout to wide screen and menu item
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## Embeddings App
	 Embedding testing application.
	'''
    }
    st.set_page_config(layout="wide", menu_items=menu_items)


    embeddings_name = f"embeddings-{generate_random_string()}"

    # with st.expander("Add a single document to the knowledge base", expanded=True):
    #     st.write("For heavy or long PDF, please use the 'Add documents in batch' option below.")
    #     st.checkbox("Translate document to English", key="translate2")
    #     uploaded_file = st.file_uploader("Upload a document to add it to the knowledge base", type=['pdf','jpeg','jpg','png', 'txt'])
    #     if uploaded_file is not None:
    #         llm_helper = LLMHelper(index_name=embeddings_name)
    #         # To read file as bytes:
    #         bytes_data = uploaded_file.getvalue()
    #         print("------------------- bytes data -------------------")
    #         print(bytes_data)

    #         if st.session_state.get('filename', '') != uploaded_file.name:
    #             upload_file(bytes_data, uploaded_file.name)
    #             converted_filenames = [""]
    #             if uploaded_file.name.endswith('.txt'):
    #                 # Add the text to the embeddings
    #                 llm_helper.add_embeddings_lc(st.session_state['file_url'])

    #             else:
    #                 # Get OCR with Layout API and then add embeddigns
    #                 converted_filenames = llm_helper.convert_file_and_add_embeddings_demo(st.session_state['file_url'], st.session_state['file_url_witout_sas'], st.session_state['filename'], st.session_state['translate'])
                
    #             llm_helper.blob_client.upsert_blob_metadata(
    #                 uploaded_file.name, 
    #                 {
    #                     'converted': 'true', 
    #                     'embeddings_added': 'true',
    #                     'converted_filename': f'{converted_filenames[0] if converted_filenames else ""}',
    #                     # 'converted_filename': f"{[base64.b64encode(f.encode('utf-8')).decode('utf-8') for f in converted_filenames]}"
    #                     # 'converted_filename': f"{[f for f in converted_filenames]}"
    #                 }
    #             )
    #             st.success(f"File {uploaded_file.name} embeddings added to the knowledge base.")
            
    #         pdf_display = f'<iframe src="{st.session_state["file_url"]}" width="700" height="1000" type="application/pdf"></iframe>'

    with st.expander("Add a single document to the knowledge base split by bookmarks", expanded=True):
        st.write("For heavy or long PDF, please use the 'Add documents in batch' option below.")
        st.checkbox("Translate document to English", key="translate")
        uploaded_file = st.file_uploader("Upload a document to add it to the knowledge base", type=['pdf','jpeg','jpg','png', 'txt'], key="uploader2")
        if uploaded_file is not None:
            llm_helper = LLMHelper(index_name=embeddings_name)
            # To read file as bytes:
            bytes_data = uploaded_file.getvalue()
            # print("------------------- bytes data -------------------")
            # print(bytes_data)

            if st.session_state.get('filename', '') != uploaded_file.name:
                upload_file(bytes_data, uploaded_file.name)
                st.session_state['file_path'] = downloaded_pdf_path = download_pdf(st.session_state['file_url'])
                converted_filenames = [""]
                if uploaded_file.name.endswith('.txt'):
                    # Add the text to the embeddings
                    llm_helper.add_embeddings_lc(st.session_state['file_url'])

                else:
                    # Get OCR with Layout API and then add embeddigns
                    converted_filenames = llm_helper.convert_file_and_add_embeddings_bookmarks(st.session_state['file_path'], st.session_state['file_url'], st.session_state['file_url_witout_sas'], st.session_state['filename'], st.session_state['translate'])
                
                llm_helper.blob_client.upsert_blob_metadata(
                    uploaded_file.name, 
                    {
                        'converted': 'true', 
                        'embeddings_added': 'true',
                        'converted_filename': f'{converted_filenames[0] if converted_filenames else ""}',
                        'embeddings': embeddings_name,
                        # 'converted_filename': f"{[base64.b64encode(f.encode('utf-8')).decode('utf-8') for f in converted_filenames]}"
                        # 'converted_filename': f"{[f for f in converted_filenames]}"
                    }
                )
                st.success(f"File {uploaded_file.name} embeddings added to the knowledge base.")
            
            pdf_display = f'<iframe src="{st.session_state["file_url"]}" width="700" height="1000" type="application/pdf"></iframe>'


except Exception as e:
    st.error(traceback.format_exc())
