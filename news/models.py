from django.db import models
from urllib import urlencode
from django.template.defaultfilters import slugify
from boost_consulting.utils.docinfo_writer import *
from utils.cache import eternal_cache as cache
import os
import sys
import datetime
import stat
import sets
from time import strptime

class NewsWriter(DocInfoExtractWriter):
    docinfo_fields = ('date', 'summary')

class News(models.Model):
    title = models.CharField(maxlength=100)
    slug = models.SlugField(maxlength=50)
    summary = models.CharField(maxlength=300)
    body = models.TextField()
    date = models.DateField()

    def get_title(self):
        self._scan()
        return self.title

    class Meta:
        verbose_name_plural = 'news'
        ordering = ['-date']

    # Don't allow admin; it's misleading since we're actually reading from
    # files.
    
    # class Admin:
    #    date_hierarchy = 'date'
    #    list_display = ('title', 'date')
    #    ordering = ('-date',)

    def __str__(self):
        return self.summary

    def get_absolute_url(self):
        return self.date.strftime('/news/%Y/%b/%d/') + self.slug

    content_path = 'content/news'

    @classmethod
    def _scan(self):
        try:
            mod_time = os.stat(self.content_path)[stat.ST_MTIME]
        except:
            return []

        if mod_time == cache.get('news_mod_time'):
            return

        try:
            files = os.listdir(self.content_path)
        except:
            files = []

        print 'rescanning news..'

        for item in News.objects.all():
            item.delete()

        for file in files:
            # Ignore tempfiles.
            if file.startswith('.'):
                continue

            name,ext = os.path.splitext(file)

            if not ext == '.rst':
                continue

            path = os.path.join(self.content_path, file)

            writer = NewsWriter()
            parts,data = get_parts(open(path).read().decode('utf-8'), writer)

            if not ('date' in data and 'summary' in data):
                continue

            date = data['date']
            summary = data['summary'].encode('utf-8')
            body = parts['fragment'].encode('utf-8')
            title = parts['title'].encode('utf-8')
            slug = slugify(title)

            date = strptime(date, '%Y-%m-%d')
            date = datetime.date(date[0], date[1], date[2])

            item,created = News.objects.get_or_create(slug=slug, date=date,
                defaults={'summary': summary, 'body': body, 'title': title})

            item.save()

        cache.set('news_mod_time', mod_time)

