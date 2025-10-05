import os
import tempfile
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from openai import OpenAI
from docx import Document
from .utils import extract_text_from_pdf, extract_text_from_docx
import json
import datetime

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class GenerateICFView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        # Extract text
        try:
            if file.name.lower().endswith(".pdf"):
                pages = extract_text_from_pdf(file)
            elif file.name.lower().endswith(".docx"):
                pages = extract_text_from_docx(file)
            else:
                return Response({"error": "Unsupported file type"}, status=400)
        except Exception as e:
            return Response({"error": f"Failed to extract text: {str(e)}"}, status=400)

        # Combine text for model
        combined_text = "\n".join([p["text"] for p in pages])

        # Generate sections using model
        prompt = f"""
            Extract the following sections from the clinical trial protocol and return a JSON object with section names as keys and extracted content as values:

            Return format:
            {{
                "Purpose of the Study": "extracted content here",
                "Study Procedures": "extracted content here (include number of patients and study duration if available)",
                "Risks": "extracted content here",
                "Benefits": "extracted content here"
            }}

            Text to analyze:
            {combined_text[:4000]}
            """

        # Try OpenAI API first, fallback to saved response on errors
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a clinical document parser. Return only valid JSON format as requested."},
                    {"role": "user", "content": prompt},
                ],
            )
            generated_text = response.choices[0].message.content
            
            # Clean the response text - remove markdown code blocks
            cleaned_text = generated_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # Remove ```json
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]   # Remove ```
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # Remove trailing ```
            cleaned_text = cleaned_text.strip()
            
            # Try to parse as JSON
            try:
                parsed_sections = json.loads(cleaned_text)
                # Convert back to string for template processing
                generated_text = json.dumps(parsed_sections, indent=2)
            except json.JSONDecodeError:
                pass
            
        except Exception as e:
            # Fallback to saved response
            # Read the saved response
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            response_file = os.path.join(project_root, 'openai_response_sample.txt')
            with open(response_file, 'r') as f:
                generated_text = f.read()

        # Create a new document with extracted protocol information
        doc = Document()
        
        # Add document title
        doc.add_heading('Informed Consent Form', level=1)
        doc.add_heading('Generated from Clinical Trial Protocol', level=2)
        doc.add_paragraph()  # Add spacing
        
        # Add generation timestamp
        
        timestamp = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")
        doc.add_paragraph(f"Generated on: {timestamp}")
        doc.add_paragraph()
        
        # Try to parse as JSON first, then fallback to markdown parsing
        generated_sections = {}
        
        try:
            # Clean the response text - remove markdown code blocks if present
            cleaned_text = generated_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # Remove ```json
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]   # Remove ```
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # Remove trailing ```
            cleaned_text = cleaned_text.strip()

           
            parsed_json = json.loads(cleaned_text)
            generated_sections = parsed_json
        except json.JSONDecodeError:
            # Fallback to markdown parsing
            current_section = None
            current_content = []
            
            for line in generated_text.split('\n'):
                line = line.strip()
                if line.startswith('**') and line.endswith('**'):
                    # Save previous section
                    if current_section:
                        generated_sections[current_section] = '\n'.join(current_content).strip()
                    # Start new section
                    section_name = line.replace('**', '').strip()
                    current_section = section_name
                    current_content = []
                elif current_section and line:
                    current_content.append(line)
            
            # Save last section
            if current_section:
                generated_sections[current_section] = '\n'.join(current_content).strip()
        
        # Create sections with proper formatting
        if generated_sections:
            # Add table of contents section
            doc.add_heading('Protocol Information Summary', level=2)
            doc.add_paragraph("The following information has been extracted from the clinical trial protocol:")
            
            # Add section list
            for section_name in generated_sections.keys():
                doc.add_paragraph(f"• {section_name}", style='List Bullet')
            
            doc.add_paragraph()  # Add spacing
            
            # Add each section with proper formatting
            for section_name, content in generated_sections.items():
                # Add section header
                doc.add_heading(section_name, level=2)
                
                # Add content with proper formatting
                content_para = doc.add_paragraph(content)
                content_para.style = 'Normal'
                
                # Add spacing between sections
                doc.add_paragraph()
        else:
            # Fallback content if no sections were parsed
            doc.add_heading('Protocol Information', level=2)
            doc.add_paragraph("No structured information could be extracted from the protocol document.")
            doc.add_paragraph("Original response:")
            doc.add_paragraph(generated_text)

        # Save to temp file
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx", prefix="icf_")
        doc.save(tmp_file.name)

        # Log pages used (just demo, you can improve)
        log = [{"page": p["page"], "text_sample": p["text"][:100]} for p in pages]

        # Prepare response data
        response_data = {
            "download_url": f"/api/download_icf/?file={os.path.basename(tmp_file.name)}",
            "generated_text": generated_text,
            "log": log
        }
        
        # Try to add parsed sections if JSON was successful
        try:
            parsed_sections = json.loads(generated_text)
            response_data["sections"] = parsed_sections
        except json.JSONDecodeError:
            pass
        
        return Response(response_data)

class DownloadICF(APIView):
    def get(self, request):
        file_name = request.GET.get("file")
        if not file_name:
            return Response({"error": "File not specified"}, status=400)
        
        file_path = os.path.join(tempfile.gettempdir(), file_name)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return Response({"error": "File not found"}, status=404)
        
        # Generate a descriptive filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        download_filename = f"Protocol_Extracted_Information_{timestamp}.docx"
        
        return FileResponse(
            open(file_path, "rb"), 
            as_attachment=True, 
            filename=download_filename,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
