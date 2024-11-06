import requests
from bs4 import BeautifulSoup
import psycopg2

import nltk
nltk.download('stopwords')
nltk.download('punkt_tab')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

gambling_keywords = ['casino', 'bet', 'jackpot', 'poker', 'slot', 'roulette', 'blackjack', 'gambling', 'sportsbook']

stop_words = set(stopwords.words('english'))

DATABASE = {
    'dbname': 'your_database',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'your_host',
    'port': 'your_port'
}

def init_db():
    try:
        conn = psycopg2.connect(**DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS table_name (
            url TEXT PRIMARY KEY,
            has_gambling_content BOOLEAN,
            detected_words TEXT
            );
            '''
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print('Error initializing the database: ', e)

def save_detection(url, has_gambling_content, detected_words):
    try:
        conn = psycopg2.connect(**DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO table_name (url, has_gambling_content, detected_words)
            VALUES (%s, %s, %s)
            ON CONFLICT (url)
            DO UPDATE SET has_gambling_content = EXCLUDED.has_gambling_content, detected_words = EXCLUDED.detected_words
            ''',
            (url, has_gambling_content, ', '.join(detected_words))
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error saving to the database: ", e)

def clean_text(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    return filtered_tokens

def detect_gambling_content(text):
    words = clean_text(text)
    detected_words = {word for word in words if word in gambling_keywords}
    return bool(detected_words), detected_words

def analyze_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        content = ' '.join([p.get_text() for p in soup.find_all('p')])

        has_gambling_content, detected_words = detect_gambling_content(content)
        
        save_detection(url, has_gambling_content, detected_words)

        if has_gambling_content:
            print(f"[ALERT] Situs {url} mengandung unsur perjudian: {', '.join(detected_words)}")
        else:
            print(f"[INFO] Situs {url} tidak mengandung unsur perjudian.")
            
    except Exception as e:
        print(f"Terjadi kesalahan saat menganalisis situs {url}: {e}")

init_db()

url_to_check = "https://example.com"
analyze_website(url_to_check)