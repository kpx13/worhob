# -*- coding: utf-8 -*-
from django.contrib import admin
from models import Category, Item, Image, Parametr, ParametrValue


class ParametrAdmin(admin.ModelAdmin):
    list_display = ('name', 'values')

class ImageInline(admin.StackedInline): 
    model = Image
    extra = 3

class ParametrInline(admin.StackedInline): 
    model = ParametrValue
    extra = 3
 
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'parent', 'order')

    
class ItemAdmin(admin.ModelAdmin):
    inlines = [ ImageInline, ParametrInline]
    list_display = ('name', 'art', 'category', 'price', 'at_home', 'sizes_request')
    search_fields = ['art', 'name']
    list_filter = ('category', )

admin.site.register(Parametr, ParametrAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Item, ItemAdmin)
