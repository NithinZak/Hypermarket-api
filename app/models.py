from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
import qrcode
from PIL import Image
from io import BytesIO
from django.core.files import File




# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user( email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    phone = models.IntegerField(blank=True,null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class Category(models.Model):
    category = models.CharField(max_length=30)
    image = models.ImageField(upload_to='images/category/', blank=True, null=True)

    def __str__(self):
        return self.category
    
class Product(models.Model):
    name = models.CharField(max_length=100)  # Name of the product
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Category to which the product belongs
    description = models.TextField()  # Description of the product
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the product
    offerprice = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Discounted price, if any
    quantity = models.PositiveIntegerField()  # Quantity of the product available in stock
    is_out_of_stock = models.BooleanField(default=False)  # Whether the product is out of stock
    qr_code = models.ImageField(upload_to='product_qrcodes', blank=True, null=True)  # QR code for the product
    image = models.ImageField(upload_to='images/product/', blank=True, null=True)  # Image of the product


    def save(self, *args, **kwargs):
        if self.quantity == 0:
            self.is_out_of_stock = True
        elif self.quantity > 0:
            self.is_out_of_stock = False
        if self.offerprice is not None and self.offerprice < self.price:
                if not self.offer_set.exists():
                    
                    offer = Offer(product=self)
                    offer.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.price < 0:
            raise ValidationError('Price cannot be negative')
        if self.offerprice and self.offerprice < 0:
            raise ValidationError('Offer price cannot be negative')
        if self.quantity < 0:
            raise ValidationError('Quantity cannot be negative')

@receiver(post_save, sender=Product)
def generate_qr_code(sender, instance, created, **kwargs):
        if created:  
            product_id = instance.pk
            data = product_id

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')

            instance.qr_code.save(f'product_{product_id}_qr.png', File(buffer), save=True)


class Offer(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name
    
    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        product.offerprice = product.price
        product.save()

class Purchase(models.Model):
    name = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default = 0)
    datetime = models.DateTimeField(default=timezone.now)
    total_price = models.DecimalField(decimal_places=2,max_digits=10,default=0)

    def __str__(self):
        return self.name.username
    
    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        self.product.quantity -= self.quantity
        self.product.save()
        super(Purchase, self).save(*args, **kwargs)

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField('Product', through='CartItem')
    total_price = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def update_total_price(self):
        total_price = sum(item.total_price for item in self.cartitem_set.all())
        self.total_price = total_price
        self.save()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart for {self.cart.user.username}"

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super(CartItem, self).save(*args, **kwargs)
        self.cart.update_total_price()
