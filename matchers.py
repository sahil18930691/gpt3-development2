 
import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])
