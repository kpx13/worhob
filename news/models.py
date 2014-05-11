# -*- coding: utf-8 -*-
from django.db import models
import pytils
from ckeditor.fields import RichTextField
import datetime
from dashboard import string_with_title
    
class NewsItem(models.Model):
    name = models.CharField(max_length=200, verbose_name=u'название')
    text = RichTextField(verbose_name=u'описание')
    image = models.ImageField(upload_to= 'uploads/news', blank=True, max_length=256, verbose_name=u'фото основное')
    slug = models.SlugField(max_length=200, verbose_name=u'слаг', unique=True, blank=True, help_text=u'заполнять не нужно')
    date = models.DateTimeField(default=datetime.datetime.now, verbose_name=u'дата добавления')
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug=pytils.translit.slugify(self.name)
        super(NewsItem, self).save(*args, **kwargs)
    
    @staticmethod
    def get_by_slug(page_name):
        try:
            return NewsItem.objects.get(slug=page_name)
        except:
            return None
        
    class Meta:
        verbose_name = u'новость'
        verbose_name_plural = u'новости'
        app_label = string_with_title("news", u"Новости")
    
    def __unicode__(self):
        return self.name
    
    
  
