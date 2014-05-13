# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from dashboard import string_with_title

import config
from livesettings import config_value
from django.template import Context, Template
from django.conf import settings
from django.core.mail import send_mail

def sendmail(subject, body, to_email=config_value('MyApp', 'EMAIL')):
    mail_subject = ''.join(subject)
    send_mail(mail_subject, body, settings.DEFAULT_FROM_EMAIL,
        [to_email])


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', verbose_name=u'пользователь')
    fio = models.CharField(max_length=256, verbose_name=u'ФИО или название компании')

    class Meta:
        verbose_name = u'профиль пользователя'
        verbose_name_plural = u'профили пользователей'
        app_label = string_with_title("users", u"Пользователи")
        
    def get_orderdata(self):
        r = UserOrderDataFiz.objects.filter(user=self.user)
        if r:
            return r[0]
        else:
            return None
    
    def __unicode__ (self):
        return str(self.user.username)
        
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)


class UserOrderDataFiz(models.Model):
    user = models.ForeignKey(User, related_name='orderdatafiz', verbose_name=u'пользователь')
    passport = models.CharField(max_length=512, blank=True, verbose_name=u'паспортные данные')
    address = models.CharField(max_length=255, blank=True,verbose_name=u'адрес доставки')
    contacts = models.CharField(max_length=255, blank=True,verbose_name=u'контакты')    
    field1 = models.CharField(max_length=63, blank=True,verbose_name=u'Расстояние от плеча')
    field2 = models.CharField(max_length=63, blank=True,verbose_name=u'Расстояние по внешнему шву')
    field3 = models.CharField(max_length=63, blank=True,verbose_name=u'Расстояние по внутреннему шву')
    field4 = models.CharField(max_length=63, blank=True,verbose_name=u'Обхват головы')
    field5 = models.CharField(max_length=63, blank=True,verbose_name=u'Расстояние между плечами')
    field6 = models.CharField(max_length=63, blank=True,verbose_name=u'Обхват груди')
    field7 = models.CharField(max_length=63, blank=True,verbose_name=u'Объем талии')
    field8 = models.CharField(max_length=63, blank=True,verbose_name=u'Объем бедер')

    class Meta:
        verbose_name = u'данные для заказа'
        verbose_name_plural = u'данные для заказов'
        app_label = string_with_title("users", u"Пользователи")
    
    def __unicode__ (self):
        return str(self.user.username)
