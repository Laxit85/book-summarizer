# Automatic Book Summarizer + Question Generator

This Python project extracts text from a PDF book, generates chapter summaries, and creates multiple-choice questions (MCQs) for revision.

## Features

- PDF text extraction using `pdfminer.six`
- Chapter-wise summarization using HuggingFace transformers summarization pipeline
- Simple MCQ generation for revision

## Requirements

- Python 3.7+
- Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage

Run the script with the path to your PDF file:

```bash
python book_summarizer.py path/to/your/book.pdf
```

The script will output chapter summaries and MCQs in the console.

## Notes

- The chapter splitting is based on the keyword "Chapter" in the text.
- MCQ generation is a placeholder and can be improved with more advanced NLP models.
- Summarization uses HuggingFace's default summarization model.

## License

This project is open source and free to use.
