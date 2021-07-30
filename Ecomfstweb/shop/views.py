
from django.db.models.fields import CharField
from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact, Order, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from .Paytm import Checksum
from django.contrib import messages

# Create your views here.
MERCHANT_KEY = 'Your Merchant Key'


def index(request):
    # return HttpResponse('Index shop')

    # ise category wise product ko show krne ke liye comment kiye h or ise niche line 27 ke loop me paste kiye h
    # products=Product.objects.all()
    # print(products)
    # n=len(products)
    # nSlide=n//4 + ceil((n/4) - (n//4))

    # we send list of list of products slides/list on homepage so follow the steps below:- this lit is without category
    # params={ 'no_of_slides':nSlide , 'range': range(1,nSlide), 'product': products}
    # allProds=[ [products, range(1 , nSlide), nSlide],
    #          [products, range(1, nSlide), nSlide] ]

    # list with category
    allProds=[]
    catprods=Product.objects.values('category', 'id')
    cats={item['category'] for item in catprods}
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n=len(prod)
        nSlide=n//4 + ceil((n/4) - (n//4) )
        allProds.append([prod, range(1, nSlide), nSlide])

    params={'allProds':allProds}         
    return render(request, 'shop/index.html', params)

def searchMatch(query, item):
    # return True if query matches the item 
    if query in item.desc.lower()  or query in  item.product_name.lower()  or query in item.category.lower():
        return True
    else:    
        return False
def search(request):
    query=request.GET.get('search', '')
    allProds=[]
    catprods=Product.objects.values('category', 'id')
    cats={item['category'] for item in catprods}
    for cat in cats:
        prodtemp=Product.objects.filter(category=cat)
        prod=[item for item in prodtemp if searchMatch(query, item)]
        n=len(prodtemp)
        nSlide=n//4 + ceil((n//4) - (n//4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlide), nSlide])
        params={'allProds':allProds, 'msg': ''}
        if len(allProds) == 0 :
            params={'msg':'Please make sure to enter relevant search query'}
        return render(request, 'shop/search.html', params)

def about(request):
    # return HttpResponse('We are at about page')
    return render(request, 'shop/about.html')

def contact(request):
    thank=False
    if request.method=='POST':
        name=request.POST.get('name', '')
        email=request.POST.get('email', '')
        phone=request.POST.get('phone', '')
        desc=request.POST.get('desc', '')
        if len(name)<2 or len(email)<3 or len(phone)<10 or len(desc)<5:
            messages.error(request, 'Please fill the form correctly!')
        else:
            contact=Contact(name=name, email=email, phone=phone, desc=desc)
            contact.save()
            thank = True
    return render(request, 'shop/contact.html', {'thank': thank})


def tracker(request):
    if request.method=='POST':
        orderId=request.POST.get('orderId','')
        email=request.POST.get('email', '')
        try:
            order=Order.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update=OrderUpdate.objects.filter(order_id=orderId)
                updates=[]
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response=json.dumps({"status":"Success", "updates": updates, "itemsJson":order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noItem"}')   
        except Exception as e:
            return HttpResponse('{"status":"error!"}')

    return render(request, 'shop/tracker.html')


def productView(request, myid):
    #Fetch the products using this id 
    product = Product.objects.filter(id=myid)
    print(product)
    return render(request, 'shop/prodview.html' , {'product':product[0]})

def checkout(request):
    # return HttpResponse('We are at checkout')
    if request.method =='POST':
        items_json=request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount=request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') +" " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        
        zipcode = request.POST.get('zipcode', '')
        phone = request.POST.get('phone', '')
        if len(name)<2 or len(email)<3 or len(phone)<10 or len(address)<5 or len(city)<3 or len(state)<2:
            messages.error(request, 'Please fill your details correctly to order your items! ')
        else:    
            order = Order( items_json=items_json,name=name, email=email, address=address, city=city, state=state, zip_code=zipcode, phone=phone, amount=amount)
            order.save()
            update=OrderUpdate(order_id=order.order_id, update_desc='Your order has been placed')
            update.save()
            thank = True,
            id = order.order_id
            # return render(request, 'shop/checkout.html', {'thank':thank, 'id':id})
            # Request Paytm to transfer  the amount to your account after paytm by user 

            param_dict={
                'MID':'KCqKop40419736057339',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID':email,
                'INDUSTRY_TYPE_ID':'Retail',
                'WEBSITE':'WEBSTAGING',
                'CHANNEL_ID':'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/'

            }
            param_dict['CHECKSUMHASH']= Checksum.generate_checksum(param_dict, MERCHANT_KEY)
            return render(request, 'shop/payment.html', {'param_dict':param_dict}) 
    return render(request, 'shop/checkout.html')

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form=request.POST
    response_dict={}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum=form[i]
    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    
    if verify:
        thank=False
        id=response_dict['ORDERID']
        if response_dict['RESPCODE'] == '01':
            print('order successful')
            thank=True 
            id=response_dict['ORDERID']
            
        else:
            thank=False
            print('order was not successful because'+ response_dict['RESPMSG'])
         
    return render(request, 'shop/paymentstatus.html', {'response':response_dict, 'thank':thank, 'id':id})
