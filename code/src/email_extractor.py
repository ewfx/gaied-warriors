import email
import os
from email import policy
from email.parser import BytesParser
import PyPDF2
import io
from openai import OpenAI
from PIL import Image
import base64

class EmailExtractor:
    def __init__(self, openai_api_key=None):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.openai_api_key)

    def _extract_text_from_image(self, image_content):
        """Extract text from image using OpenAI Vision API."""
        try:
            # Convert binary content to base64
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract only the text from this image without any additional commentary or prefix."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            text = response.choices[0].message.content
            # Clean up common prefixes
            prefixes_to_remove = [
                "Here is the extracted text from the image:",
                "The text in the image reads:",
                "The image contains the following text:",
                "Text from the image:"
            ]
            
            for prefix in prefixes_to_remove:
                if text.startswith(prefix):
                    text = text[len(prefix):].strip()
            
            return text.strip()
        except Exception as e:
            return f"Error extracting image text: {str(e)}"

    def extract_from_content(self, email_content: bytes):
        """Extract content from email bytes directly."""
        msg = BytesParser(policy=policy.default).parsebytes(email_content)
        
        # Extract message body
        message_body = ""
        if msg.get_body(preferencelist=('plain',)):
            message_body = msg.get_body(preferencelist=('plain',)).get_content()
        
        # Initialize attachment lists
        pdf_list = []
        image_list = []
        
        # Process attachments
        for part in msg.iter_attachments():
            filename = part.get_filename()
            if filename:
                content_type = part.get_content_type().lower()
                
                # Handle PDFs
                if content_type == 'application/pdf':
                    pdf_content = part.get_payload(decode=True)
                    pdf_text = self._extract_pdf_text(pdf_content)
                    pdf_list.append({
                        'filename': filename,
                        'text_content': pdf_text
                    })
                
                # Handle Images
                elif content_type.startswith('image/'):
                    image_content = part.get_payload(decode=True)
                    image_text = self._extract_text_from_image(image_content)
                    image_list.append({
                        'filename': filename,
                        'type': content_type,
                        'text_content': image_text
                    })
        
        return {
            'message_body': message_body,
            'pdf_list': pdf_list,
            'image_list': image_list
        }

    def extract_from_eml(self, eml_path):
        """Extract content from an EML file."""
        with open(eml_path, 'rb') as f:
            return self.extract_from_content(f.read())

    def _extract_pdf_text(self, pdf_content):
        """Extract text from PDF binary content."""
        text = ""
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
        except Exception as e:
            text = f"Error extracting PDF text: {str(e)}"
            
        return text.strip()

if __name__ == "__main__":
    import json
    extractor = EmailExtractor()
    result = extractor.extract_from_eml('C:\\tutorials\\gaied-warriors\\gaied-warriors\\code\\data\\Service request- hackathon test email.eml')
    print(json.dumps(result, indent=2))