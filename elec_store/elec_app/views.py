from django.shortcuts import render,redirect
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.contrib.auth.models import User;
from django.contrib.auth import authenticate,login,logout
from .models import Product, Cart, Address, Order
from django.db.models import Q
import re
import random
import razorpay
from django.core.mail import send_mail
# Create your views here.
def home(request):
    context={}
    products=Product.objects.all()
    context['products']=products
    print(products)
    return render(request,'home.html',context)

def ulogin(request):
    context={}
    if request.method=="POST":
        nm=request.POST["username"]
        p=request.POST["password"]
        if nm=='' or p=='':
            context["error"]="Please Fill All Required Data...!"
            return render(request,'login.html',context)
        else:
            u=authenticate(username=nm,password=p)
            print(u)
            if u !=None:
                login(request,u)
                return redirect('/home')
            else:
                context['error']="Username & Password not Matched"
                return render(request,'login.html',context)
    
        return render(request,"login.html")
    else:
        return render(request,"login.html")


def register(request):
    context = {}
    if request.method == 'POST':
        nm = request.POST['username']
        em = request.POST['email']
        p = request.POST['password']
        cp = request.POST['cpassword']

        if  nm=="" or em=="" or p=="" or cp=="":
            context["error"] = "All fields are required!"
            return render(request,'register.html',context)
        elif p != cp:
            context['error'] = "Password does not matched!"
            return render(request,'register.html',context) 
        elif len(p) < 8:
            context['error'] = "Password must be of atleast 8 characters!"
            return render(request,'register.html',context)
        else:
            try:
                u=User.objects.create(username=nm,email=em,password=p)
                u.set_password(p)
                u.save()
                return redirect('/login')
            except IntegrityError:
                context['error']="User already exists!"
                return render(request,'register.html',context)
            
    else:
        return render(request, 'register.html', context)


def product(request):
    return render(request,'product.html')
    
def ulogout(request):
    logout(request)
    return redirect('/home/')

def productdetails(request,pid):
    context={}
    prod=Product.objects.get(id=pid)
    context['product']=prod
    return render(request,'productdetails.html',context)

def addtocart(request,pid):
    product=Product.objects.get(id=pid)
    context={}
    context['product']=product
    if request.user.is_authenticated:
        p=Product.objects.get(id=pid)
        u=User.objects.get(id=request.user.id)
        q1=Q(pid=p)
        q2=Q(uid=u)
        c=Cart.objects.filter(q1&q2)
        print(c)
        print(p.pname,u.username)
        if len(c)==1:
            context['error']='Product already in cart'
            return render(request,'productdetails.html',context)
        else:
            cart=Cart.objects.create(uid=u,pid=p)
            cart.save()
            context["success"]="product added in cart successfully.."
            return render(request,'productdetails.html',context)
    else:
        context['error']='please login first'
        return render(request,'productdetails.html',context)
    
def viewcart(request):
    context={}
    carts=Cart.objects.filter(uid=request.user.id)
    context['carts']=carts
    items=0
    tprice=0
    for i in carts:
        tprice+=i.pid.price *i.qty
        items+=i.qty 

    print('total=',tprice)
    print('items=',items)
    context['total']=tprice
    context['items']=items

    return render(request,'cart.html',context)


def updateqty(request,cid,x):
    c=Cart.objects.filter(id=cid)
    quantity=c[0].qty
    if x=="1":
        quantity+=1
    elif quantity>1:
        quantity-=1
    c.update(qty=quantity)
    return redirect("/mycart")

def removecart(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect("/mycart")



def checkaddress(request):
    context={}
    u=User.objects.get(id=request.user.id)
    addrss=Address.objects.filter(user_id=u)
    if len(addrss) >=1:
        return redirect("/placeorder")
    else:
        if request.method=="POST":
            fn=request.POST["full_name"]
            ln=request.POST['last_name']
            ad=request.POST["address"]
            mo=request.POST["mobile"]
            ct=request.POST["city"]
            st=request.POST["state"]
            pc=request.POST["pincode"]
            print(fn,ad,mo,ct,st,pc)
            if fn=="" or ln=="" or ad=="" or mo=="" or ct=="" or st=="" or pc=="":
                context["error"]='All Fields are Required'
                return render(request,"address.html",context)
            elif not fn.isalpha() and fn.isspace():
                context['error']='Only Letter are Allowed in First Name'
                return render(request,'address.html',context)
            elif not ln.isalpha() and fn.isspace():
                context['error']='Only Letter are Allowed in Last Name'
                return render(request,'address.html',context)
            elif not ct.isalpha():
                context['error']='Only Letter are Allowed in City'
                return render(request,'address.html',context)
            elif not ct.isalpha():
                context['error']='Only Letter are Allowed in State'
                return render(request,'address.html',context)
            elif not re.match('[6-9]\d{9}',mo):
                context['error']='Invalid Mobile Number'
                return render(request,'address.html',context)
            else:
                address=Address.objects.create(user_id=u,fullname=fn,lastname=ln,address=ad,mobile=mo,city=ct,state=st,pincode=pc)
                address.save()
                return redirect('/placeorder')
    return render(request,"address.html",context)


def placeorder(request):
    user=User.objects.get(id=request.user.id)
    c=Cart.objects.filter(uid=user)
    context={}
    for i in c:
        oid=random.randint(1000,9999)
        total_amt=i.qty * i.pid.price
        add=Order.objects.create(user_id=user,order_id=oid,qty=i.qty,p_id=i.pid,amt=total_amt)
        print('Order Created')
        add.save()
    c.delete()
    return redirect('/fetchorder')



def fetchorder(request):
    user=User.objects.get(id=request.user.id)
    address=Address.objects.filter(user_id=user)
    q1=Q(user_id=user)
    q2=Q(payment_status='unpaid')
    orders=Order.objects.filter(q1&q2)
    total_amt=0
    quantity=0
    for i in orders:
        total_amt+=i.amt
        quantity+=i.qty
    
    context={}
    context['items']=quantity
    context['total']=total_amt
    context['address']=address
    context['orders']=orders
    return render(request,'fetchorder.html',context)

def makepayment(request):
    context={}
    user=User.objects.get(id=request.user.id)
    address=Address.objects.filter(user_id=user)
    q1=Q(user_id=user)
    q2=Q(payment_status='unpaid')
    orders=Order.objects.filter(q1&q2)
    total_amt=0
    for i in orders:
        total_amt+=i.amt
    
    client = razorpay.Client(auth=("rzp_test_pkKhenE3rkKZxE", "zxf8KkMnHdKodtJyoXg1ll0t"))

    data = { "amount": total_amt*100, "currency": "INR", "receipt": "order_rcptid_11" }
    payment = client.order.create(data=data)
    context['payment']=payment
    return render(request,"pay.html",context)
    

def mailsend(request):
    send_mail(
    "Order Cinfirmation",
    "Dear Customers, \n Your Order is Confirmed and Will be Dileverd Soon.",
    "patilchirag424@gmail.com",
    ["chiragpatil050620@gmail.com"],
    fail_silently=False,
)
    return redirect('/home/')


def filterbyprice(request):
    context={}
    mn=request.GET["min"]
    mx=request.GET["max"]
    q1=Q(price__gte=mn)
    q2=Q(price__lte=mx)
    products=Product.objects.filter(q1&q2)
    context['products']=products
    return render(request,'product.html',context)

def filterbycategory(request,cat):
    context={}
    products=Product.objects.filter(category=int(cat))
    context['products']=products
    if len(products)==0:
        context['error']="No Products Available"
        return render(request,'home.html',context)
    else:
        return render(request,'home.html',context)
    

def viewproduct(requets):
    context={}
    products=Product.objects.all()
    context['products']=products
    return render(requets,'viewproduct.html',context)