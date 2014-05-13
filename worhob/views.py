# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, HttpResponseNotFound, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms.util import ErrorList
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime

from pages.models import Page
from news.models import NewsItem
from catalog.models import Category, Item
from shop.models import Cart, Order
from shop.forms import OrderForm
from sessionworking import SessionCartWorking
from users.forms import OrderDataFizForm
from slideshow.models import Slider

NEWS_PAGINATION_COUNT = 10


def get_common_context(request):
    c = {}
    c['request_url'] = request.path
    c['user'] = request.user
    c['categories'] = Category.objects.filter(parent=None).extra(order_by = ['order'])
    c['categories_all'] = Category.objects.all()
    c['categories_all_count_1'] = Category.objects.all().count() / 3
    c['categories_all_count_2'] = Category.objects.all().count() * 2 / 3
    c['categories_all_count_3'] = Category.objects.all().count()
    c['news_recent'] = NewsItem.objects.all()[0:3]
    c['price_from'] = 0
    c['price_to'] = 50000 
    
    if request.user.is_authenticated():
        c['cart_working'] = Cart
        Cart.update(request.user, SessionCartWorking(request).pop_content())
    else:
        c['cart_working'] = SessionCartWorking(request)
    c['cart_count'], c['cart_sum'] = c['cart_working'].get_goods_count_and_sum(request.user)
    c['cart_content'] = c['cart_working'].get_content(request.user)
    c['slideshow'] = Slider.objects.all()
    c.update(csrf(request))
    
    return c

def reset_catalog(request):
    for i in request.session.keys():
        if i.startswith('catalog_'):
            del request.session[i]

def catalog(request):
    c = get_common_context(request)
    return render_to_response('catalog_map.html', c, context_instance=RequestContext(request))

def home_page(request):
    c = get_common_context(request)
    reset_catalog(request)
    c['request_url'] = 'home'
    c['slideshow'] = Slider.objects.all()
    c['items_at_home'] = Item.objects.filter(at_home=True)
    c.update(Page.get_page_by_slug('home'))
    return render_to_response('home.html', c, context_instance=RequestContext(request))

def news(request, slug=None):
    c = get_common_context(request)
    reset_catalog(request)
    if slug == None:
        items = NewsItem.objects.all()
        paginator = Paginator(items, NEWS_PAGINATION_COUNT)
        page = int(request.GET.get('page', '1'))
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            page = 1
            items = paginator.page(page)
        except EmptyPage:
            page = paginator.num_pages
            items = paginator.page(page)
        c['page'] = page
        c['page_range'] = paginator.page_range
        if len(c['page_range']) > 1:
            c['need_pagination'] = True
        
        c['news'] = items
        return render_to_response('news.html', c, context_instance=RequestContext(request))
    else:
        c['new'] = NewsItem.get_by_slug(slug)
        return render_to_response('new.html', c, context_instance=RequestContext(request))


def category(request, slug):
    c = get_common_context(request)
    if slug:
        c['category'] = Category.get_by_slug(slug)
        items = Item.objects.filter(category__in=c['category'].get_descendants(include_self=True))
    else:
        items = Item.objects.all()
    
    c['items'] = items
    return render_to_response('catalog.html', c, context_instance=RequestContext(request))

def category_filter(request, slug):
    c = get_common_context(request)
    if 'category' in request.POST:
        slug = request.POST['category']
    if slug:
        c['category'] = Category.get_by_slug(slug)
        items = Item.objects.filter(category__in=c['category'].get_descendants(include_self=True))
        for k in request.POST.keys():
            if k.startswith('parametr_'):
                p_id = k[9:]
                p_value = request.POST[k]
                if p_id == 'price_from' and p_value:
                    items = items.filter(price__gte=float(p_value))
                    c['price_from'] = int(p_value)
                elif p_id == 'price_to' and p_value:
                    items = items.filter(price__lte=float(p_value))
                    c['price_to'] = int(p_value)
                else:
                    items = Item.filter_by_parametr(items, p_id, p_value)
    else:
        items = Item.objects.all()
    if 'q' in request.POST:
        items = items.filter(name__icontains=request.POST['q'])
    
    c['items'] = items
    return render_to_response('catalog.html', c, context_instance=RequestContext(request))

def item(request, slug):
    c = get_common_context(request)
    if request.method == 'POST':
        if request.POST['action'] == 'add_in_basket':
            c['cart_working'].add_to_cart(request.user, request.POST['item_id'], 1)
        return HttpResponseRedirect(request.get_full_path())
    c['item'] = Item.get_by_slug(slug)
    c['category'] = c['item'].category
    c['same'] = Item.objects.filter(category__in=c['category'].get_descendants(include_self=True)).order_by('?')[0:4]
    c['in_cart'] = c['cart_working'].present_item(request.user, c['item'].id)
    return render_to_response('item.html', c, context_instance=RequestContext(request))

def cart(request):
    c = get_common_context(request)
    if request.method == 'POST':
        if request.POST['action'] == 'del_from_basket':
            c['cart_working'].del_from_cart(request.user, request.POST['item_id'])
            return HttpResponseRedirect(request.get_full_path())
        elif request.POST['action'] == 'set_count':
            try:
                c['cart_working'].set_count(request.user, request.POST['item_id'], request.POST['set_count'])
            except:
                pass
            return HttpResponseRedirect(request.get_full_path())
        elif request.POST['action'] == 'plus':
            c['cart_working'].count_plus(request.user, request.POST['item_id'])
            return HttpResponseRedirect(request.get_full_path())
        elif request.POST['action'] == 'minus':
            c['cart_working'].count_minus(request.user, request.POST['item_id'])
            return HttpResponseRedirect(request.get_full_path())
        elif request.POST['action'] == 'to_order':
            comment = request.POST['comment']
            deliv = int(request.POST['deliver'])
                
            Order(user=request.user,
                  comment=comment).save()
            return HttpResponseRedirect('/')
    
    if 'count' in request.GET:
        request.session['catalog_cart_count'] = request.GET['count']
    if 'catalog_cart_count' in request.session:
        c['count'] = request.session['catalog_cart_count']
    else:
        request.session['catalog_cart_count'] = 10
        c['count'] = 10
    
    items = c['cart_working'].get_content(request.user)
    
    c['sizes_request'] = False
    for oc in items:
        if oc['item'].sizes_request:
            c['sizes_request'] = True 
    
    paginator = Paginator(items, request.session['catalog_cart_count'])
    page = int(request.GET.get('page', '1'))
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        items = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        items = paginator.page(page)
    c['page'] = page
    c['page_range'] = paginator.page_range
    if len(c['page_range']) > 1:
        c['need_pagination'] = True
    
    c['items'] = items
    
    return render_to_response('cart.html', c, context_instance=RequestContext(request))

def order(request):
    c = get_common_context(request)
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/cart/')
    profile = request.user.get_profile()
    module = OrderDataFizForm
    
    if request.method == 'GET':
        form = module(instance=profile.get_orderdata(), initial={'fio': profile.fio})
        orderform = OrderForm()
    if request.method == 'POST':
        form = module(request.POST, instance=profile.get_orderdata())
        orderform = OrderForm(request.POST)            
        if form.is_valid() and orderform.is_valid():
            f = form.save(commit=False)
            f.user = request.user
            f.save()
            profile.fio = form['fio'].value()
            profile.save()
            of = orderform.save(commit=False)
            of.user = request.user
            of.savecommit()
            return HttpResponseRedirect('/order-ok/')
        
    c['form'] = form
    c['orderform'] = orderform
    return render_to_response('order_fiz.html', c, context_instance=RequestContext(request))


def lk(request):
    c = get_common_context(request)
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    profile = request.user.get_profile()
    module = OrderDataFizForm
    form = module(instance=profile.get_orderdata(), initial={'fio': profile.fio})
    if request.method == 'GET':
        c['form'] = form
    if request.method == 'POST':
        form = module(request.POST, instance=profile.get_orderdata())            
        if form.is_valid():
            f = form.save(commit=False)
            f.user = request.user
            f.save()
            profile.fio = form['fio'].value()
            profile.save()
            return HttpResponseRedirect('/lk/')
    c['form'] = form
    return render_to_response('lk_fiz.html', c, context_instance=RequestContext(request))
    

def other_page(request, page_name):
    reset_catalog(request)
    c = get_common_context(request)
    try:
        c.update(Page.get_page_by_slug(page_name))
        return render_to_response('page.html', c, context_instance=RequestContext(request))
    except:
        raise Http404()

def search(request):
    c = get_common_context(request)
    if request.method == 'POST':
        q = request.POST.get('q', '')
        if q:
            c['q'] = q
            c['s_categories'] = Category.search(q)
            c['s_items'] = Item.search(q)
            return render_to_response('search_res.html', c, context_instance=RequestContext(request))
    return HttpResponseRedirect('/')

def sitemap(request):
    c = get_common_context(request)
    return render_to_response('sitemap.html', c, context_instance=RequestContext(request))
