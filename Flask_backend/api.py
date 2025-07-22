import spacy
from textblob import TextBlob
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline

emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None  
)

nlp = spacy.load("en_core_web_lg")
sia = SentimentIntensityAnalyzer()

# Named Entity Recognition
def ner(text):
    doc = nlp(text)
    print([(ent.text, ent.label_) for ent in doc.ents]) 
    return [{'entity': ent.text, 'category': ent.label_} for ent in doc.ents]

# Sentiment Analysis
def sentiment_analysis(text):
    blob = TextBlob(text)
    return blob.sentiment

def vader_sentiment(text):
    return sia.polarity_scores(text)


def emotion_detection(text):
    return emotion_classifier(text)[0]  # Returns list of emotions with scores