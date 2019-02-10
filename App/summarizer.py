"""from gensim.summarization import summarize

class summarizer:
    def __init__(self, text = ""):
        self.text = text
    def summary(self):
        return summarize(self.text)"""
    
class Summarizer:
    
    def __init__(self):
        pass
    
    def summarize_article(self,articles):
        summaries = []
        from gensim.summarization import summarize
        for article in articles:
            summary = summarize(article)
            summaries.append(summary)
        
        return summaries

