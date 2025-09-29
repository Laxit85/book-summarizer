import os
import re
from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from transformers import pipeline

def extract_text_from_pdf(pdf_path):
    output_string = StringIO()
    with open(pdf_path, 'rb') as f:
        extract_text_to_fp(f, output_string, laparams=LAParams(), output_type='text', codec=None)
    return output_string.getvalue()

def extract_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        return f.read()

def split_into_chapters(text):
    # Simple heuristic: split by "Chapter" keyword followed by number or title
    chapters = re.split(r'(Chapter\s+\d+[^\\n]*)', text, flags=re.IGNORECASE)
    # The split will create a list where chapter titles and content alternate
    chapter_texts = []
    if len(chapters) > 1:
        # Combine title and content pairs
        for i in range(1, len(chapters), 2):
            title = chapters[i].strip()
            content = chapters[i+1].strip() if i+1 < len(chapters) else ""
            chapter_texts.append((title, content))
    else:
        # If no chapters found, treat whole text as one chapter
        chapter_texts.append(("Full Text", text))
    return chapter_texts

def generate_summary(text, summarizer):
    # Handle empty or very short text gracefully
    if not text or len(text.strip()) == 0:
        return "No content to summarize."
    # HuggingFace summarizer has max token limits, so truncate if too long
    max_chunk = 2000
    text = text.strip()
    if len(text) > max_chunk:
        text = text[:max_chunk]
    # Increase max_length to allow longer summaries (3-4 paragraphs)
    summary = summarizer(text, max_length=500, min_length=150, do_sample=False)
    return summary[0]['summary_text']

import random

def generate_mcqs(summary, question_generator):
    # Generate questions from summary text
    # For simplicity, generate 3 questions per summary
    questions = []
    sentences = [s.strip() for s in summary.split('. ') if s.strip()]
    for i, sentence in enumerate(sentences[:3]):
        question = f"What is the main idea of: '{sentence}'?"
        # Use the sentence as the correct answer
        correct_answer = sentence
        # Generate distractors by picking other sentences or dummy options
        distractors = []
        for s in sentences:
            if s != sentence and s not in distractors:
                distractors.append(s)
            if len(distractors) >= 3:
                break
        # If not enough distractors, add generic ones
        while len(distractors) < 3:
            distractors.append("Other option")
        options = distractors + [correct_answer]
        random.shuffle(options)
        questions.append({
            "question": question,
            "options": options,
            "answer": correct_answer
        })
    return questions

def main(file_path, return_results=False):
    print(f"Extracting text from {file_path} ...")
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif ext == '.txt':
        text = extract_text_from_txt(file_path)
    else:
        print("Unsupported file format. Please provide a PDF or TXT file.")
        return None if return_results else None

    print("Splitting text into chapters...")
    chapters = split_into_chapters(text)
    print(f"Found {len(chapters)} chapters/sections.")

    print("Loading summarization model...")
    summarizer = pipeline("summarization")

    # For question generation, we can use a QA pipeline or a text2text generation model
    # Here, we just simulate MCQs for demonstration
    question_generator = None

    results = []
    for title, content in chapters:
        print(f"Processing {title} ...")
        summary = generate_summary(content, summarizer)
        mcqs = generate_mcqs(summary, question_generator)
        results.append({
            "chapter": title,
            "summary": summary,
            "mcqs": mcqs
        })

    if return_results:
        return results

    # Output results
    for res in results:
        print(f"\n{res['chapter']}")
        print("Summary:")
        print(res['summary'])
        print("\nMCQs:")
        for i, q in enumerate(res['mcqs']):
            print(f"Q{i+1}: {q['question']}")
            for opt in q['options']:
                print(f" - {opt}")
            print(f"Answer: {q['answer']}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python book_summarizer.py <path_to_pdf_or_txt>")
        sys.exit(1)
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        sys.exit(1)
    main(file_path)
