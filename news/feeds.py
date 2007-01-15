from django.contrib.syndication.feeds import Feed
from models import News

class NewsFeed(Feed):
    title = 'Boost Consulting News'
    link = 'http://..'
    description = 'The latest news from Boost Consulting'

    def items(self):
        return News.objects.all()[:10]

