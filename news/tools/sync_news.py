from boost_consulting.news.models import *
from boost_consulting.utils.docinfo_writer import *
from django.template.defaultfilters import slugify
import os
import sys
import datetime
from time import strptime

class NewsWriter(DocInfoExtractWriter):
    docinfo_fields = ('date', 'summary')

news_path = '../../content/news/'

try:
    files = os.listdir(news_path)
except:
    files = []

for file in files:
    # Ignore tempfiles.
    if file.startswith('.'):
        continue

    name,ext = os.path.splitext(file)

    if not ext == '.rst':
        continue

    path = os.path.join(news_path, file)
    print path

    writer = NewsWriter()

    parts,data = get_parts(open(path).read().decode('utf-8'), writer)

    date = data['date']
    summary = data['summary'].encode('utf-8')
    body = parts['fragment'].encode('utf-8')
    title = parts['title'].encode('utf-8')
    slug = slugify(title)

    date = strptime(date, '%Y-%m-%d')
    date = datetime.date(date[0], date[1], date[2])

    entry,_ = News.objects.get_or_create(title=title,
        defaults={'date': date, 'summary': summary, 'body': body, 'slug': slug})

    entry.date = date
    entry.summary = summary
    entry.body = body
    entry.save()

