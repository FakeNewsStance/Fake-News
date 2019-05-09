from newsapi.newsapi_client import NewsApiClient
from newspaper import Article
import api_creds

class NewsArticles:
    def __init__(self):
        self.newsapi = NewsApiClient(api_key=api_creds.news_api_key)
        
    def get_urls(self,query):
        all_articles = self.newsapi.get_everything(q=query,
                                      language='en',
                                      sort_by='relevancy',page=1)
        urls = []
        for article in all_articles['articles']:
            urls.append(article['url'])

        return urls

    def get_articles(self,query):
        urls = self.get_urls(query)
        articles = []
        for url in urls[:10]:
            try:
                fetched_article = Article(url)
                fetched_article.download()
                fetched_article.parse()
                articles.append(fetched_article.text)
            except:
                pass
        return articles


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

