import feedparser
import logging
import os
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from celery import Celery
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import datetime

# Initialize NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Database 
DATABASE_URL = 'postgresql://postgres:Risha2512%40@localhost:5432/newsarticle_db'  # Update this with your database info
Base = declarative_base()
from sqlalchemy import Column, Integer, String, DateTime

# Define Article model
class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    link = Column(String) 
    content = Column(Text, nullable=False)
    published_date = Column(TIMESTAMP, nullable=False)
    category = Column(String(50), nullable=True)

# Set up the database engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Initialize Celery
from celery import Celery

celery_app = Celery('main', broker='redis://localhost:6379/0')


# RSS feed URLs
RSS_FEEDS = [
    'http://rss.cnn.com/rss/cnn_topstories.rss',
    'http://qz.com/feed',
    'http://feeds.foxnews.com/foxnews/politics',
    'http://feeds.reuters.com/reuters/businessNews',
    'http://feeds.feedburner.com/NewshourWorld',
    'https://feeds.bbci.co.uk/news/world/asia/india/rss.xml',
]




# Set up logging
logging.basicConfig(level=logging.INFO)

# SQLAlchemy setup
Base = declarative_base()


# Define the Article model
class Article(Base):
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)  # Title cannot be null
    link = Column(String, nullable=False, unique=True)  # Link must be unique
    published = Column(DateTime, nullable=False)  # Published date cannot be null
    summary = Column(Text, nullable=True)  # Summary can be null
    category = Column(String, nullable=False)  # Category can be null

# Database connection string (update this with your actual connection details)
DATABASE_URL = 'postgresql://postgres:Risha2512%40@localhost/newsarticle_db'

# Create a new SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create all tables in the database
Base.metadata.create_all(engine)

# Create a new session
session = Session()

# You can now use the session to add data or perform queries


# Create a database session
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def classify_article(article):
    """Classify the article into predefined categories."""
    tokens = word_tokenize(article['summary'].lower())  # Use summary or content here
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]

    # categorization 
    if any(keyword in filtered_tokens for keyword in ['terrorism', 'protest', 'riot', 'unrest']):
        return 'Terrorism / Protest / Political Unrest / Riot'
    elif any(keyword in filtered_tokens for keyword in ['positive', 'uplifting', 'good', 'great']):
        return 'Positive/Uplifting'
    elif 'natural' in filtered_tokens and 'disaster' in filtered_tokens:
        return 'Natural Disasters'
    else:
        return 'Others'


# fetching articles from an RSS feed
def fetch_articles(feed_urls):
    articles = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            
            article = {
                'title': entry.title,
                # Check if 'summary' or 'description' is present
                'summary': getattr(entry, 'summary', getattr(entry, 'description', 'No summary available')),
                'link': entry.link,  # Assuming you need the link
                'published': entry.published if 'published' in entry else 'No publish date',
                'content': entry.content[0].value if 'content' in entry and entry.content else '',
            }
            # Classify the article
            category = classify_article(article)  # Pass the whole article
            article['category'] = category
            articles.append(article)
    return articles





    
@celery_app.task
def process_articles(articles):
    """Process articles and store them in the database."""
    session = Session()
    
    for article in articles:
        # Check for duplicates
        existing_article = session.query(Article).filter_by(title=article['title'], published_date=article['published']).first()
        
        if existing_article is None:
            category = classify_article(article)  # Classifying based on the content
            
            new_article = Article(
                title=article['title'],
                link=article['link'],
                content=article['summary'],  # Assuming summary is content for simplicity
                published_date=article['published'],
                category=category
            )
            session.add(new_article)
            logging.info(f"Article added: {article['title']} - Category: {category}")
        else:
            logging.info(f"Duplicate article found: {existing_article.title}")

    session.commit()
    session.close()




# Function to save articles to CSV
def save_articles_to_csv(articles):
    # Create a DataFrame from the list of articles
    df = pd.DataFrame(articles)

    
    expected_columns = ['title', 'link', 'published', 'summary', 'category']
    
    # Assign default values if the DataFrame doesn't contain all expected columns
    for col in expected_columns:
        if col not in df.columns:
            df[col] = None  
    
   
    df.to_csv('articles.csv', columns=expected_columns, index=False)

def main():
    feed_urls = [
        "http://rss.cnn.com/rss/cnn_topstories.rss",
        "http://qz.com/feed",
        "http://feeds.foxnews.com/foxnews/politics",
        "http://feeds.reuters.com/reuters/businessNews",
        "http://feeds.feedburner.com/NewshourWorld",
        "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"
    ]
    
    articles = fetch_articles(feed_urls)
    save_articles_to_csv(articles)

if __name__ == '__main__':
    main()
# Create the database tables
Base.metadata.create_all(engine)  


@celery_app.task
def process_articles(articles):
    """Process articles and store them in the database."""
    session = Session()
    
    for article in articles:
        # Check for duplicates
        existing_article = session.query(Article).filter_by(title=article['title'], published_date=article['published_date']).first()
        
        if existing_article is None:
            category = classify_article(article)
            new_article = Article(
                title=article['title'],
                link=article['link'],
                content=article['summary'],
                published_date=article['published'],
                category=category
            )
            session.add(new_article)
            logging.info(f"Article added: {article['title']} - Category: {category}")
        else:
            logging.info(f"Duplicate article found: {existing_article.title}")

    session.commit()
    session.close()

def main():
    try:
        logging.info("Starting the news collection application.")
        
        articles = fetch_articles(RSS_FEEDS)  # Fetch the articles from RSS feeds
        if articles:
            process_articles.delay(articles)  # Send articles to the Celery queue for processing
        
        logging.info("News collection application finished.")
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    Base.metadata.create_all(engine)  # Create tables if they do not exist
    main()






