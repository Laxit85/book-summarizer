import os
import sys
import tempfile
from django.shortcuts import render
from django.conf import settings
from transformers import pipeline
from .models import Contact
from django.http import HttpResponseRedirect
from django.urls import reverse

# Add path to import from parent directory
sys.path.append(os.path.join(settings.BASE_DIR, '..'))
from book_summarizer import extract_text_from_pdf, extract_text_from_txt, split_into_chapters, generate_summary, generate_mcqs

def home(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            if ext not in ['.pdf', '.txt']:
                return render(request, 'ui/index.html', {'error': 'Please upload a PDF or TXT file.'})

            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name

            try:
                # Extract text
                if ext == '.pdf':
                    text = extract_text_from_pdf(temp_path)
                else:
                    text = extract_text_from_txt(temp_path)

                # Split into chapters
                chapters = split_into_chapters(text)

                # Load summarizer
                summarizer = pipeline("summarization")

                results = []
                for title, content in chapters:
                    summary = generate_summary(content, summarizer)
                    mcqs = generate_mcqs(summary, None)  # question_generator not used
                    results.append({
                        'chapter': title,
                        'summary': summary,
                        'mcqs': mcqs
                    })

                # Pass results to separate result page
                return render(request, 'ui/result.html', {'results': results})

            except Exception as e:
                return render(request, 'ui/index.html', {'error': f'Error processing file: {str(e)}'})

            finally:
                # Clean up temp file
                os.unlink(temp_path)

        elif 'name' in request.POST and 'email' in request.POST and 'message' in request.POST:
            name = request.POST.get('name')
            email = request.POST.get('email')
            message = request.POST.get('message')
            # Save contact message to database
            Contact.objects.create(name=name, email=email, message=message)
            # Render index with success message
            return render(request, 'ui/index.html', {'success': 'Message sent successfully!'})
    return render(request, 'ui/index.html')
