from django.db import models

# Create your models here.
class Product(models.Model):
    CAT=((1,'Mobile'), (2,'Accesories'),(3,'Wireless Gadgets'),(4,'Laptops'),(5,'Television'),(6,'Fridges'),(7,'Air Conditioners'),(8,'Cameras and Accessiories'))
    pname=models.CharField(max_length=50)
    price=models.FloatField(verbose_name="Price")
    description=models.TextField(max_length=500,verbose_name="Description")
    category=models.IntegerField(choices=CAT,verbose_name="Category")
    is_active=models.BooleanField(default=True,verbose_name="IS_Available")
    pimage=models.ImageField(upload_to='images')

class Cart(models.Model):
    uid=models.ForeignKey('auth.User',on_delete=models.CASCADE,db_column='uid')
    pid=models.ForeignKey('Product',on_delete=models.CASCADE,db_column='pid')
    qty=models.IntegerField(default=1)

class Address(models.Model):
    user_id=models.ForeignKey("auth.User",on_delete=models.CASCADE,db_column='user_id')
    address=models.CharField(max_length=400)
    fullname=models.CharField(max_length=80)
    lastname=models.CharField(max_length=90)
    city=models.CharField(max_length=20)
    state=models.CharField(max_length=30)
    pincode=models.CharField(max_length=10)
    mobile=models.CharField(max_length=10)

class Order(models.Model):
    order_id=models.CharField(max_length=50)
    user_id=models.ForeignKey("auth.User",on_delete=models.CASCADE, db_column="user_id")
    p_id=models.ForeignKey("Product",on_delete=models.CASCADE,db_column="p_id")
    qty=models.IntegerField(default=1)
    amt=models.FloatField()
    payment_status=models.CharField(max_length=20,default="unpaid")