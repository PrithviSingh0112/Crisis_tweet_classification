"""
Text Extraction and Analysis Pipeline
Author: Prithvi Singh Dangas
Date: 2025-05-19

Usage:
1. Install dependencies: pip install -r requirements.txt
2. Run: python text_analysis.py --input Input.xlsx --output final_output.xlsx
"""
import argparse
import os
import re
import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup
from readability import Document
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import textstat
from textblob import TextBlob
from tqdm import tqdm
from charset_normalizer import from_bytes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('pipeline.log'), logging.StreamHandler()]
)

class TextAnalyzer:
    def __init__(self):
        self.stopwords = self._load_stopwords()
        self.positive_words, self.negative_words = self._load_sentiment_words()

    def _load_stopwords(self, folder='StopWords'):
        stopwords = set()
        for fname in os.listdir(folder):
            path = os.path.join(folder, fname)
            try:
                with open(path, 'rb') as f:
                    content = f.read()
                    result = from_bytes(content).best()
                    if result and hasattr(result, 'text'):
                        stopwords.update(result.text.lower().split())
                    else:
                        stopwords.update(content.decode('latin-1', errors='ignore').lower().split())
            except Exception as e:
                logging.error(f"Error loading {fname}: {str(e)}")
        return stopwords

    def _load_sentiment_words(self, folder='MasterDictionary'):
        try:
            positive = set()
            negative = set()
            
            # Load positive words
            with open(os.path.join(folder, 'positive-words.txt'), 'rb') as f:
                content = f.read()
                result = from_bytes(content).best()
                if result and hasattr(result, 'text'):
                    positive = set(result.text.lower().split())
                else:
                    positive = set(content.decode('latin-1', errors='ignore').lower().split())
            
            # Load negative words
            with open(os.path.join(folder, 'negative-words.txt'), 'rb') as f:
                content = f.read()
                result = from_bytes(content).best()
                if result and hasattr(result, 'text'):
                    negative = set(result.text.lower().split())
                else:
                    negative = set(content.decode('latin-1', errors='ignore').lower().split())
                    
            return positive, negative
        except Exception as e:
            logging.error(f"Error loading sentiment words: {str(e)}")
            return set(), set()

    def extract_article(self, url):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            doc = Document(response.text)
            soup = BeautifulSoup(doc.summary(), 'html.parser')
            
            # Clean unwanted elements
            for element in soup(['script', 'style', 'header', 'footer', 'nav']):
                element.decompose()
                
            title = doc.title()
            body = ' '.join([p.get_text(strip=True) for p in soup.find_all(['p', 'h1', 'h2', 'h3'])])
            
            return f"{title}\n\n{body}"
        except Exception as e:
            logging.error(f"Failed to extract {url}: {str(e)}")
            return ''

    def analyze_text(self, text):
        analysis = {
            'POSITIVE SCORE': 0,
            'NEGATIVE SCORE': 0,
            'POLARITY SCORE': 0.0,
            'SUBJECTIVITY SCORE': 0.0,
            'AVG SENTENCE LENGTH': 0.0,
            'PERCENTAGE OF COMPLEX WORDS': 0.0,
            'FOG INDEX': 0.0,
            'AVG NUMBER OF WORDS PER SENTENCE': 0.0,
            'COMPLEX WORD COUNT': 0,
            'WORD COUNT': 0,
            'SYLLABLE PER WORD': 0.0,
            'PERSONAL PRONOUNS': 0,
            'AVG WORD LENGTH': 0.0
        }

        try:
            # Text preprocessing
            sentences = [sent for sent in sent_tokenize(text) if sent.strip()]
            words = [word.lower() for word in word_tokenize(text) 
                    if word.isalpha() and word.lower() not in self.stopwords]

            if not sentences or not words:
                raise ValueError("Insufficient text for analysis")

            # Sentiment analysis
            analysis['POSITIVE SCORE'] = sum(1 for w in words if w in self.positive_words)
            analysis['NEGATIVE SCORE'] = sum(1 for w in words if w in self.negative_words)
            
            blob = TextBlob(text)
            analysis['POLARITY SCORE'] = blob.sentiment.polarity
            analysis['SUBJECTIVITY SCORE'] = blob.sentiment.subjectivity

            # Readability metrics
            analysis['WORD COUNT'] = len(words)
            analysis['AVG SENTENCE LENGTH'] = len(words) / len(sentences)
            analysis['AVG NUMBER OF WORDS PER SENTENCE'] = analysis['AVG SENTENCE LENGTH']
            
            complex_words = [w for w in words if textstat.syllable_count(w) > 2]
            analysis['COMPLEX WORD COUNT'] = len(complex_words)
            analysis['PERCENTAGE OF COMPLEX WORDS'] = len(complex_words) / len(words)
            analysis['FOG INDEX'] = 0.4 * (analysis['AVG SENTENCE LENGTH'] + analysis['PERCENTAGE OF COMPLEX WORDS'])

            # Additional metrics
            analysis['SYLLABLE PER WORD'] = sum(textstat.syllable_count(w) for w in words) / len(words)
            analysis['PERSONAL PRONOUNS'] = len(re.findall(r'\b(I|we|my|ours|us|me|our|ourselves)\b', text, re.I))
            analysis['AVG WORD LENGTH'] = sum(len(w) for w in words) / len(words)

        except Exception as e:
            logging.error(f"Analysis error: {str(e)}")

        return analysis

def main(input_path, output_path):
    """Main execution flow"""
    try:
        # Initialize components
        analyzer = TextAnalyzer()
        nltk.download('punkt', quiet=True)

        # Create articles directory
        os.makedirs('articles', exist_ok=True)

        # Load input data
        df = pd.read_excel(input_path)
        results = []

        # Process URLs
        for _, row in tqdm(df.iterrows(), total=len(df)):
            url_id = row['URL_ID']
            url = row['URL']
            
            # Extract and save article
            article_text = analyzer.extract_article(url)
            
            # Save to text file
            with open(f'articles/{url_id}.txt', 'w', encoding='utf-8') as f:
                f.write(article_text)
            
            # Perform analysis
            analysis = analyzer.analyze_text(article_text)
            results.append({**row.to_dict(), **analysis})

        # Save results
        output_df = pd.DataFrame(results)
        output_df.to_excel(output_path, index=False)
        logging.info(f"Successfully saved results to {output_path}")

    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    main(args.input, args.output)