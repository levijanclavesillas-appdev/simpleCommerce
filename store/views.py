from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
import json
import datetime
import random

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

from .utils import cookieCart, product_sales_pipeline
from .models import *


def store(request):

    products = Product.objects.all()

    context = {'products': products}
    return render(request, 'store/store.html', context)


def cart(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
       
    context = {'items': items, 'order': order}
    return render(request, 'store/cart.html', context)

def checkout(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        cookieData = cookieCart(request)
        order = cookieData['order']
        items = cookieData['items']

    if request.POST.get('make-payment-btn') == 'make-payment-btn':
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
        else:
            cookieData = cookieCart(request)
            order = cookieData['order']
        if request.user.is_authenticated:
            stripe_url = product_sales_pipeline(order.id, 10000)
        else:
            stripe_url = product_sales_pipeline(random.random(), 20000)
        return HttpResponseRedirect(stripe_url)
        
    context = {'items': items, 'order': order}
    return render(request, 'store/checkout.html', context)

def cancelled(request):
    return render(request, 'store/cancelled.html')

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = orderItem.quantity + 1
    elif action == 'remove':
        orderItem.quantity = orderItem.quantity - 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item added", safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    
    else:

        name = data['form']['name']
        email = data['form']['email']

        cookieData = cookieCart(request)
        items = cookieData['items']

        customer, created = Customer.objects.get_or_create(
            email=email
        )
        customer.name = name
        customer.save()

        order = Order.objects.create(
            customer = customer,
            complete = False,
        )

        for item in items:
            product = Product.objects.get(id=item['product']['id'])

            orderItem = OrderItem.objects.create(
                product = product,
                order = order,
                quantity = item['quantity']
            )

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
        )


    return JsonResponse("Payment processed", safe=False)