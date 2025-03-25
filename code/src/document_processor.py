import json
import os
from typing import List, Dict, Union
from langchain_openai import ChatOpenAI, OpenAI
from email_extractor import EmailExtractor

class DocumentProcessor:
    def __init__(self, api_key: str):
        self.client = ChatOpenAI()
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        with open('email_classifier_prompt.txt', 'r') as file:
            template = file.read()
            # Validate template contains required placeholders
            required_vars = ['@@@document1@@@']
            for var in required_vars:
                if var not in template:
                    raise ValueError(f"Prompt template missing required variable: {var}")
            return template

    def process_documents(self, documents: List[str]) -> List[Dict]:

        # Escape any backticks in the documents
        escaped_docs = [doc.replace("`", "\\`") for doc in documents]
        
        try:
            formatted_prompt = self.prompt_template
            for i, doc in enumerate(escaped_docs, 1):
                formatted_prompt = formatted_prompt.replace(f"@@@document{i}@@@", doc)
        except Exception as e:
            raise ValueError(f"Unexpected error formatting prompt: {e}")

        model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        response = model.invoke(formatted_prompt)

        try:
            raw_content = response.content
            
            if not raw_content:
                raise ValueError("Empty response from LLM")
                
            return json.loads(raw_content)
            
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON response from LLM")

    def process_email(self, email_content: bytes) -> Dict:
        """Process email and its attachments to classify the request"""
        extractor = EmailExtractor()
        email_data = extractor.extract_from_content(email_content)
        
        # Combine all text content
        all_text = [email_data['message_body']]
        
        # Add PDF contents
        for pdf in email_data['pdf_list']:
            all_text.append(pdf['text_content'])
            
        # Add Image contents
        for img in email_data['image_list']:
            all_text.append(img['text_content'])
            
        # Process combined text
        combined_text = "\n".join(filter(None, all_text))
        return self.process_single_document(combined_text)

    def process_single_document(self, document: str) -> Dict:
       return self.process_documents([document])[0]
