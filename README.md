# News-Article-Aggregator
This project is a comprehensive News Article Aggregator that fetches, classifies, and stores articles from multiple RSS feeds, allowing users to stay informed about current events efficiently.

## Key Features
RSS Feed Integration: Collects articles from multiple trusted news sources, including CNN, Reuters, and BBC.
Article Classification: Implements Natural Language Processing (NLP) to categorize articles based on keywords and sentiment analysis.
Database Management: Utilizes SQLAlchemy to store articles in a PostgreSQL database, ensuring efficient data retrieval and management.
Data Persistence: Allows for duplicate detection to prevent redundant entries in the database.
Data Export: Provides functionality to export collected articles into a CSV file for further analysis or reporting.
Celery Integration: Implements Celery for asynchronous processing of articles, enhancing performance and scalability.

## Technologies Used
Python: Primary programming language for developing the application.
NLTK: Natural Language Toolkit for processing and analyzing textual data.
SQLAlchemy: ORM for managing database interactions.
PostgreSQL: Database management system for storing articles.
Celery: Asynchronous task queue for handling article processing.
Feedparser: Library for parsing RSS feeds.
