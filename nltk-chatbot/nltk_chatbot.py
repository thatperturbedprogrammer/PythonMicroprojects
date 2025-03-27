import nltk
import random
import string
import numpy as np
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Sample chatbot responses
responses = {
    "greeting": ["Hello! How can I assist you today?", "Hi there! What can I do for you?"],
    "goodbye": ["Goodbye! Have a great day!", "Bye! Take care."],
    "thanks": ["You're welcome!", "No problem! Always happy to help."],
    "unknown": ["I'm not sure I understand. Can you rephrase that?", "Sorry, I didn't get that."],
    "technology": ["Technology is evolving rapidly! What aspect interests you?", "AI, Blockchain, or Cybersecurity—what are you curious about?"],
    "philosophy": ["Philosophy is deep! Do you prefer existentialism or stoicism?", "The unexamined life is not worth living—thoughts?", "No man was ever wise by chance..."]
}

# Predefined patterns for basic responses
patterns = {
    "greeting": ["hello", "hi", "hey", "greetings"],
    "goodbye": ["bye", "goodbye", "see you"],
    "thanks": ["thank you", "thanks", "appreciate it"],
    "technology": ["tech", "AI", "machine learning", "blockchain", "cybersecurity", "coding", "programming"],
    "philosophy": ["philosophy", "meaning of life", "existentialism", "stoicism", "ethics", "morality", "truth"]
}

# Load and preprocess data
lemmatizer = WordNetLemmatizer()
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in string.punctuation]
    return tokens

def get_response(user_input):
    user_tokens = preprocess_text(user_input)
    
    # Check for predefined responses
    for key, values in patterns.items():
        if any(word in user_tokens for word in values):
            return random.choice(responses[key])
    
    # Use cosine similarity for more dynamic responses
    corpus = list(responses.keys()) + [user_input]
    vectorizer = CountVectorizer().fit_transform(corpus)
    similarity_matrix = cosine_similarity(vectorizer[-1], vectorizer[:-1])
    
    best_match = np.argmax(similarity_matrix)
    if similarity_matrix[0, best_match] > 0:
        return random.choice(responses[corpus[best_match]])
    
    return random.choice(responses["unknown"])

# Running the chatbot
def chatbot():
    print("Chatbot: Hello! Type 'exit' to end the chat.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break
        response = get_response(user_input)
        print(f"Chatbot: {response}")

if __name__ == "__main__":
    chatbot()
