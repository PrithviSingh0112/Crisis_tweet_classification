
# Text Analysis Pipeline

This repository contains a Python-based pipeline for automated extraction and linguistic analysis of online articles. It performs sentiment, readability, and complexity analysis on text content sourced from URLs provided in an Excel sheet.

## 📌 Author
Prithvi Singh Dangas  
🗓️ Date: May 2025

---

## 🚀 Features

- Automated article extraction from URLs
- Sentiment analysis using custom dictionaries
- Readability metrics including Fog Index, Syllable Count, etc.
- Regex-based personal pronoun detection
- Saves extracted articles as `.txt` files
- Exports results to an Excel file

---

## 🗂️ Project Structure

```
Root/
├── text_analysis.py
├── requirements.txt
├── Input.xlsx
├── articles/               # Auto-created folder for saved articles
├── StopWords/
│   ├── StopWords_Auditor.txt
│   ├── StopWords_Currencies.txt
│   └── ...
├── MasterDictionary/
│   ├── positive-words.txt
│   └── negative-words.txt
└── final_output.xlsx       # Generated after script execution
```

---

## 📥 Installation

Make sure Python 3.8+ is installed.

```bash
pip install -r requirements.txt
```

---

## 🛠️ Usage

Run the script with the required input and output file paths:

```bash
python text_analysis.py --input Input.xlsx --output final_output.xlsx
```

- `Input.xlsx`: Excel file with columns `URL_ID` and `URL`
- `final_output.xlsx`: Excel file to save analysis results

---

## 📊 Metrics Computed

| Metric                    | Description |
|---------------------------|-------------|
| POSITIVE SCORE            | Count of positive words |
| NEGATIVE SCORE            | Count of negative words |
| POLARITY SCORE            | (Pos - Neg) / (Pos + Neg + ε) |
| SUBJECTIVITY SCORE        | (Pos + Neg) / Total Words |
| AVG SENTENCE LENGTH       | Total Words / Sentence Count |
| COMPLEX WORD COUNT        | Words with >2 syllables |
| PERCENTAGE COMPLEX WORDS  | % of complex words |
| FOG INDEX                 | 0.4 * (Avg Sentence Length + % Complex Words) |
| SYLLABLE PER WORD         | Total Syllables / Words |
| PERSONAL PRONOUNS         | Regex match for I, we, my, ours, etc. |
| AVG WORD LENGTH           | Total Characters / Words |

---

## 🧱 Dependencies

```
pandas==1.3.5
requests==2.26.0
beautifulsoup4==4.10.0
readability-lxml==0.8.1
nltk==3.6.7
textstat==0.7.0
textblob==0.15.3
tqdm==4.62.3
charset-normalizer==2.0.12
openpyxl==3.0.10
python-docx==0.8.11
```

---

## ⚠️ Error Handling

- Network timeouts handled via try/except
- Charset normalization for encoding issues
- Empty or invalid content is skipped with warnings
- All file I/O is wrapped with error-safe handling

---

## 📄 License

This project is open for academic and non-commercial use. Attribution required.
