# Personalized News Anchor

An AI-powered application that creates personalized news presentations.

## Project Structure

personalized-news-anchor/
├── backend/ # Django backend
├── frontend/ # Frontend application
├── ai_models/ # AI/ML models and processing
├── docs/ # Documentation
└── README.md


### Fetch general news
http://127.0.0.1:8000/api/fetch-news/

### Fetch technology news
http://127.0.0.1:8000/api/fetch-news/?category=technology

### All articles
http://127.0.0.1:8000/api/articles/

### Technology articles only
http://127.0.0.1:8000/api/articles/?category=technology

### Search for "apple"
http://127.0.0.1:8000/api/articles/?search=apple

### Get Chategories
http://127.0.0.1:8000/api/categories/

### Clear news
http://127.0.0.1:8000/api/clear-news/


### business - Business news
### entertainment - Entertainment news
### general - General news (default)
### health - Health and medical news
### science - Science and research news
### sports - Sports news
### technology - Technology news

### Go to newsapi.org
###Register for a free account
###Get your API key
###Add it to your .env file

### For starting Application
python manage.py runserver