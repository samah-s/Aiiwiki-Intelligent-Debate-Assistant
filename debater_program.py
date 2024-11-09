import requests
from bs4 import BeautifulSoup
import re

class IntelligentDebater:
    def __init__(self, topic):
        self.topic = topic
        self.knowledge_base = []

    def fetch_wiki_content(self, topic):
        """Fetch content from Wikipedia for the given topic."""
        url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print("Error fetching Wikipedia content.")
            return ""

    def extract_sentences(self, wiki_content):
        """Extract sentences from the Wikipedia content."""
        soup = BeautifulSoup(wiki_content, 'html.parser')
        paragraphs = soup.find_all('p')
        sentences = []
        for paragraph in paragraphs:
            text = paragraph.get_text()
            sentences += re.split(r'(?<=[.!?]) +', text)
        return sentences

    def keyword_extraction(self, argument):
        """Extract keywords from the user argument, handling negations."""
        words = argument.lower().split()
        keywords = []
        negated_keywords = []
        
        for i, word in enumerate(words):
            if word == "not" or word == "no":
                # Take the word following "no" or "not" as a negated keyword
                if i + 1 < len(words):
                    negated_keywords.append(words[i + 1])
            else:
                keywords.append(word)
        
        return keywords, negated_keywords

    def build_knowledge_base(self, user_argument=None):
        """Build a knowledge base using keywords from the topic and the user argument."""
        keywords, negated_keywords = self.keyword_extraction(user_argument or self.topic)
        
        wiki_content = self.fetch_wiki_content(self.topic)
        sentences = self.extract_sentences(wiki_content)
        
        scored_sentences = []
        for sentence in sentences:
            # Score sentences based on the presence of argument-related keywords
            score = sum(1 for keyword in keywords if keyword in sentence.lower())
            neg_score = sum(1 for neg_keyword in negated_keywords if neg_keyword in sentence.lower())
            
            # Adjust score if negated keywords are present
            if score > 0 or neg_score > 0:
                total_score = score - neg_score
                if total_score > 0:
                    scored_sentences.append((sentence.strip(), total_score))

        # Sort sentences based on score and take the top 6 most relevant ones
        top_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[:16]
        self.knowledge_base = [sentence for sentence, score in top_sentences]

    def fetch_antonyms(self, word):
        """Fetch antonyms for a given word from Thesaurus.com."""
        url = f"https://www.thesaurus.com/browse/{word}"
        response = requests.get(url)
        
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        antonyms_section = soup.find_all('a', class_='css-1gyuw4i eh475bn0')
        antonyms = [antonym.get_text() for antonym in antonyms_section]

        return antonyms

    def find_rebuttal(self, user_argument):
        """Find rebuttals based on the user's argument and generate a propositional logic-based response."""
        keywords, negated_keywords = self.keyword_extraction(user_argument)
        matched_sentences = []

        for sentence in self.knowledge_base:
            # Check for keyword matches or negation-based rebuttals in the sentence
            if any(keyword in sentence.lower() for keyword in keywords) or \
               any(neg_keyword in sentence.lower() for neg_keyword in negated_keywords):
                matched_sentences.append(sentence)

        if matched_sentences:
            return self.generate_best_rebuttal(matched_sentences, user_argument)
        else:
            return "I couldn't find a relevant rebuttal for that argument."

    def generate_best_rebuttal(self, matched_sentences, user_argument):
        """Generate the best rebuttal using propositional logic from matched sentences."""
        propositions = [self.create_proposition(sentence) for sentence in matched_sentences]
        
        # Analyze the propositions and assign scores
        scored_propositions = [(prop, self.score_proposition(prop, user_argument)) for prop in propositions]
        
        # Sort propositions based on score and take the top 2
        top_rebuttals = sorted(scored_propositions, key=lambda x: x[1], reverse=True)[:2]
        
        return "\n".join([rebuttal for rebuttal, score in top_rebuttals])

    def create_proposition(self, sentence):
        """Create a propositional representation from a sentence."""
        clean_sentence = sentence.strip().lower().capitalize()
        return clean_sentence  # Use the cleaned sentence as a simple proposition

    def fetch_synonyms(self, word):
        """Fetch synonyms for a given word from Thesaurus.com."""
        url = f"https://www.thesaurus.com/browse/{word}"
        response = requests.get(url)
        
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        synonyms_section = soup.find_all('a', class_='css-1gyuw4i eh475bn0')
        synonyms = [synonym.get_text() for synonym in synonyms_section]

        return synonyms

    def score_proposition(self, proposition, user_argument):
        """Score the proposition based on its relevance to the user's argument, considering negation and antonyms."""
        score = 0
        keywords, negated_keywords = self.keyword_extraction(user_argument)

        # Increase score for keyword matches
        for keyword in keywords:
            if keyword in proposition:
                score += 1
            synonyms = self.fetch_synonyms(keyword)
            for synonym in synonyms:
                if synonym in proposition:
                    score += 1

        # Handle negated keywords by checking antonyms
        for neg_keyword in negated_keywords:
            antonyms = self.fetch_antonyms(neg_keyword)
            for antonym in antonyms:
                if antonym in proposition:
                    score += 1

        return score

    def debate(self):
        """Start the debate."""
        print(f"Welcome to the Intelligent Debater on the topic: {self.topic}\n")
        while True:
            user_argument = input("Enter your argument (or type 'exit' to quit): ")
            if user_argument.lower() == 'exit':
                print("Debate ended.")
                break

            # Build the knowledge base with the user's current argument
            self.build_knowledge_base(user_argument)
            rebuttal = self.find_rebuttal(user_argument)
            print(f"\nRebuttal: {rebuttal}\n")

