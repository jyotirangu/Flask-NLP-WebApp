import spacy
from textblob import TextBlob
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline

emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True
)

nlp = spacy.load("en_core_web_sm")
sia = SentimentIntensityAnalyzer()

# Named Entity Recognition
def ner(text):
    doc = nlp(text)
    return [{'entity': ent.text, 'category': ent.label_} for ent in doc.ents]



# Sentiment Analysis
def sentiment_analysis(text):
    blob = TextBlob(text)
    return blob.sentiment

def vader_sentiment(text):
    return sia.polarity_scores(text)


# # Emotion Detection (Basic using TextBlob polarity)
# emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)

def emotion_detection(text):
    results = emotion_classifier(text)[0]  # Get list of emotions
    top_emotion = max(results, key=lambda x: x['score'])
    return top_emotion
