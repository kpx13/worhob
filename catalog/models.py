# -*- coding: utf-8 -*-

from mptt.models import MPTTModel, TreeForeignKey
from django.db import models
from ckeditor.fields import RichTextField
import pytils
from pytils import translit
import datetime
from dashboard import string_with_title
from django.db.models import Q


class Parametr(models.Model):
    name = models.CharField(max_length=127, verbose_name=u'название')
    values = models.TextField(default=u'', blank=True, verbose_name=u'возможные значения', 
                             help_text=u"Введите возможные значения с новой строки. Если значение должен ввести пользователь, то не надо.")
    
    def get_values(self):
        return [x.strip() for x in self.values.split('\n') if x.strip()]

    
    class Meta:
        verbose_name = u'параметр'
        verbose_name_plural = u'параметры'
        app_label = string_with_title("catalog", u"Каталог")
        
    def __unicode__(self):
        return self.name 

class Category(MPTTModel):
    name = models.CharField(max_length=127, verbose_name=u'название')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', verbose_name=u'родительская категория')
    parametrs = models.ManyToManyField(Parametr, null=True, blank=True, verbose_name=u'параметры')
    desc = models.TextField(default=u'', blank=True, null=True, verbose_name=u'описание')
    order = models.IntegerField(null=True, blank=True, default=0, verbose_name=u'порядок сортировки')
    slug = models.SlugField(max_length=127, verbose_name=u'слаг', unique=True, blank=True, help_text=u'заполнять не нужно')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug=pytils.translit.slugify(self.name)
        super(Category, self).save(*args, **kwargs)
        if self.order == 0:
            self.order = self.id
            self.save()
    
    @staticmethod
    def get_by_slug(page_name):
        try:
            return Category.objects.get(slug=page_name)
        except:
            return None
        

    def breadcrumb(self):
        page = self
        breadcrumbs = []
        while page:
            breadcrumbs.append(page)
            page = page.parent
        breadcrumbs.reverse()
        return breadcrumbs[:-1]
    
    @staticmethod
    def has_id_1c(id_1c):
        return Category.objects.filter(id_1c=id_1c).count() > 0
    
    @staticmethod
    def get_by_id_1c(id_1c):
        if id_1c:
            return Category.objects.filter(id_1c=id_1c)[0]
        else:
            return None
        
    class Meta:
        verbose_name = u'категория'
        verbose_name_plural = u'категории'
        app_label = string_with_title("catalog", u"Каталог")

    
    class MPTTMeta:
        order_insertion_by = ['name']
        
    def __unicode__(self):
        return '%s%s' % (' -- ' * self.level, self.name)
    
    @staticmethod
    def get(id_):
        try:
            return Category.objects.get(id=id_)
        except:
            return None
        
    @staticmethod
    def search(query):
        return Category.objects.filter(Q(name__icontains=query))


class Item(models.Model):
    category = models.ForeignKey(Category, verbose_name=u'категория', related_name='items')
    name = models.CharField(max_length=512, verbose_name=u'название')
    art = models.CharField(max_length=50, verbose_name=u'артикул')
    price = models.FloatField(verbose_name=u'цена')
    description = RichTextField(default=u'', blank=True, verbose_name=u'описание')
    sizes_request = models.BooleanField(blank=True, default=False, verbose_name=u'запросить точные размеры?')
    order = models.IntegerField(null=True, blank=True, verbose_name=u'порядок сортировки')
    at_home = models.BooleanField(blank=True, default=False, verbose_name=u'показывать на главной')
    slug = models.SlugField(max_length=128, verbose_name=u'слаг', unique=True, blank=True, help_text=u'заполнять не нужно')
    date = models.DateTimeField(default=datetime.datetime.now, verbose_name=u'дата добавления')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug=pytils.translit.slugify(self.art)
        if self.order == 0:
            self.order = self.id
            self.save()
        super(Item, self).save(*args, **kwargs)
    
    @staticmethod
    def get_by_slug(page_name):
        try:
            return Item.objects.get(slug=page_name)
        except:
            return None
    
    @staticmethod    
    def filter_by_parametr(items, p_id, p_value):
        res = []
        if not (p_id and p_value):
            return items
        try:
            par = Parametr.objects.get(id=p_id)
        except:
            return items
        for i in items:
            pv = ParametrValue.objects.filter(item=i, parametr=par)
            if len(pv) > 0: # есть значение параметра
                if pv[0].value.strip() == p_value.strip():
                    res.append(i)
        return res

    @staticmethod
    def get(id_):
        try:
            return Item.objects.get(id=id_)
        except:
            return None
        
    @staticmethod
    def search(query):
        return Item.objects.filter(Q(name__icontains=query) |
                                   Q(art__icontains=query) |
                                   Q(description__icontains=query) |
                                   Q(description_bottom__icontains=query))
    
    @staticmethod
    def get_home():
        return Item.objects.filter(at_home=True, in_archive=False)
    
    def same_category(self):
        return Item.objects.filter(category=self.category, in_archive=False).exclude(id = self.id)
    
    def get_path(self):
        path = [self.category]
        while path[0].parent:
            path.insert(0, path[0].parent)
        return path
    
    class Meta:
        verbose_name = u'товар'
        verbose_name_plural = u'товары'
        ordering=['order']
        app_label = string_with_title("catalog", u"Каталог")
        
    def __unicode__(self):
        return self.name


class Image(models.Model):
    item = models.ForeignKey(Item, verbose_name=u'товар', related_name='image')
    image = models.ImageField(upload_to=lambda instance, filename: 'uploads/items/' + translit.translify(filename),
				max_length=256, blank=True, verbose_name=u'изображение')
    order = models.IntegerField(null=True, blank=True, default=100, verbose_name=u'порядок сортировки')

    @staticmethod
    def get(id_):
        try:
            return Item.objects.get(id=id_)
        except:
            return None
    
    class Meta:
        verbose_name = u'изображение'
        verbose_name_plural = u'изображения'
        ordering=['order']
        app_label = string_with_title("catalog", u"Каталог")
        
    def __unicode__(self):
        return str(self.id) 



class ParametrValue(models.Model):
    item = models.ForeignKey(Item, verbose_name=u'товар', related_name='parametr')
    parametr = models.ForeignKey(Parametr, verbose_name=u'параметр')
    value = models.CharField(max_length=128, verbose_name=u'значение')

    class Meta:
        verbose_name = u'значение параметра'
        verbose_name_plural = u'значения параметров'
        app_label = string_with_title("catalog", u"Каталог")
        
