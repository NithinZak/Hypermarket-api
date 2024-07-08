from django.contrib import admin
from .models import CustomUser,Product,Category,Purchase,Cart,CartItem,Purchase,Offer

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Purchase)
admin.site.register(Offer)

