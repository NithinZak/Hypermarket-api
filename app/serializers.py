
from rest_framework import serializers
from . import models
from django.contrib.auth import authenticate


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = models.CustomUser
        fields = ['username', 'email', 'password','first_name','last_name']

    def create(self, validated_data):
        user = models.CustomUser.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class ProductListSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='id')
    class Meta:
        model = models.Product
        fields = '__all__'



class ProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='id',required=False)
    class Meta:
        model = models.Product
        fields =['name','category','description','price','quantity','is_out_of_stock','product_id'] 

class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields =['name','category','description','price','quantity','is_out_of_stock','offerprice']
    category = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    is_out_of_stock = serializers.BooleanField(required=False)
    offerprice = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)

class ProductDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = []

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['id','password','email','username','first_name','last_name','is_active','is_staff','is_superuser','date_joined','phone']

class PurchaseListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='name.username', read_only=True)
    productname = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = models.Purchase
        fields = '__all__'

class PaymentListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='name.username', read_only=True)
    productname = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = models.Purchase
        fields = ['total_price','productname','username']



# user ---------------------------------------------------------------------------

class CartItemSerializer(serializers.ModelSerializer):
    productname = serializers.CharField(source='product.name', read_only=True)
    price = serializers.DecimalField(source='product.price',decimal_places=2, max_digits=10, read_only=True)
    user = serializers.CharField(source='cart.user', read_only=True)
    user_id = serializers.IntegerField(source='cart.user.id', read_only=True)
    total_price = serializers.DecimalField(source='cart.total_price',decimal_places=2, max_digits=10, read_only=True)
    class Meta:
        model = models.CartItem
        fields = ['id', 'cart', 'productname', 'quantity','user','total_price','price','user_id']

class CartItemDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = []

class ListOfferSerializer(serializers.ModelSerializer):
    productname = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = models.Offer
        fields = '__all__'

class BuyProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Purchase
        fields = ['name','product','quantity']

class productDetailSerializer(serializers.ModelSerializer):
    categoryname = serializers.CharField(source='category.category', read_only=True)
    product_id = serializers.IntegerField(source='id', read_only=True)
    class Meta:
        model = models.Product
        fields = ['name','categoryname','description','price','offerprice','is_out_of_stock','product_id']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'

class AddToPurchaseSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Purchase
        fields = ['name','product','quantity',]