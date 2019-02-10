"""from gensim.summarization import summarize

class summarizer:
    def __init__(self, text = ""):
        self.text = text
    def summary(self):
        return summarize(self.text)"""
    
from sumy.parsers.plaintext import PlaintextParser 
from sumy.nlp.tokenizers import Tokenizer 
from sumy.summarizers.lex_rank import LexRankSummarizer 

file = "plain_text.txt" 
parser = PlaintextParser.from_file(file, Tokenizer("english"))
summarizer = LexRankSummarizer()

summary = summarizer(parser.document, 5)
