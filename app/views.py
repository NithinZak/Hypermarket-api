

from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from . import serializers 
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from . import models
from rest_framework.views import APIView
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class RegistrationView(generics.CreateAPIView):
    serializer_class = serializers.RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'phone':user.phone
        })
    
class UserLoginView(generics.GenericAPIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'is_staff': user.is_staff,
                'is_admin': user.is_superuser
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        


#admin start--------------------------------------------------------------

class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        try:
            serializer = serializers.ProductSerializer(data=request.data)
            if serializer.is_valid():
                if serializer.validated_data['quantity'] == 0:
                    serializer.validated_data['is_out_of_stock'] = True
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        except:
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

    
    def get(self, request, format=None):
        try:
            products = models.Product.objects.all()
            serializer = serializers.ProductSerializer(products, many=True)
            if serializer.data:
                return Response({"status": 1, "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"status": 0, "Message": "No product"}, status=status.HTTP_204_NO_CONTENT)
        except models.Product.DoesNotExist:
            logger.error("No products found")
            return Response({"status": 0, "Message": "No product found"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"Message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class ProductUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.ProductUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = models.Product.objects.all()

class ProductDelete(generics.DestroyAPIView):
    serializer_class = serializers.ProductDeleteSerializer
    permission_classes = [IsAuthenticated]
    queryset = models.Product.objects.all()
    
class ProductOutOfStock(APIView):
    permission_classes =[IsAuthenticated]
    def get(self, request, format=None):
        try:
            products = models.Product.objects.filter(quantity__lt=10)
            serializer = serializers.ProductSerializer(products, many = True)
            if serializer.data:
                return Response({"status":1,"data":serializer.data},status=status.HTTP_200_OK)
            else:
                return Response({"status":0,"Message":"No Products"},status=status.HTTP_200_OK)
        except:
            return Response({"error":"Somthing went wrong"})
        
class UserList(APIView):
    permission_classes =[IsAuthenticated]
    def get(self, request, format=None):
        users = models.CustomUser.objects.all()
        serializer = serializers.UserListSerializer(users, many = True)
        if serializer.data:
            return Response({"status":1,"data":serializer.data},status=status.HTTP_200_OK)
        else:
            return Response({"status":0,"Message":"No User"},status=status.HTTP_200_OK)
    
class PurchaseList(APIView):
    permission_classes =[IsAuthenticated]
    def get(self, request, format=None):
        purchases = models.Purchase.objects.all()
        serializer = serializers.PurchaseListSerializer(purchases, many = True)
        if serializer.data:
            return Response({"status":1,"data":serializer.data},status=status.HTTP_200_OK)
        else:
            return Response({"status":0,"Message":"No Purchases"},status=status.HTTP_200_OK)

class PaymentList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        payments = models.Purchase.objects.all()
        serializer = serializers.PaymentListSerializer(payments, many = True)
        if serializer.data:
            return Response({"status":1,"data":serializer.data},status=status.HTTP_200_OK)
        else:
            return Response({"status":0,"Message":"No Payments"},status=status.HTTP_200_OK)

#user start--------------------------------------------------------------- 

class DesplayProducts(APIView):
    serializer_class = serializers.ProductListSerializer
    permission_classes = [IsAuthenticated]

    def get(self,request, format=None):
        try:
            queryset = models.Product.objects.all()
            serializer = self.serializer_class(queryset, many=True)
            if serializer.data:
                return Response({"status":1,"data":serializer.data},status=status.HTTP_200_OK)
            else:
                return Response({"status":0,"Message":"No products"},status=status.HTTP_200_OK)
        except:
            return Response({"Message":"somthing went wrong"})

class ListOffers(APIView):
    serializer_class = serializers.ListOfferSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self,request,format=None):
        try:
            queryset = models.Offer.objects.all()
            serializer = self.serializer_class(queryset, many=True)
            if serializer.data:
                return Response({"status":1,"data":serializer.data},status=status.HTTP_200_OK)
            else:
                return Response({"status":0,"Message":"No Offer"})

        except models.Offer.DoesNotExist:
            return Response({"Message":"No Offer"})

class AddToCart(generics.CreateAPIView):
    permission_classes =[IsAuthenticated]
    serializer_class = serializers.CartItemSerializer

    def post(self, request, *args, **kwargs):     
        user = request.user
        product_id = self.kwargs.get('product_id')
        products = get_object_or_404(models.Product, pk=product_id)
        quantity = self.kwargs.get('quantity')
        if quantity <= products.quantity:
            if not product_id:
                return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                cart = models.Cart.objects.get(user=user)
            except models.Cart.DoesNotExist:
                cart = models.Cart.objects.create(user=user)
            product = models.Product.objects.get(pk=product_id)  
            try:
                cart_item = models.CartItem.objects.get(cart=cart, product=product)
                cart_item.quantity += quantity
                cart_item.save()
            except models.CartItem.DoesNotExist:
                cart_item = models.CartItem.objects.create(cart=cart, product=product, quantity=quantity)

            serializer = self.get_serializer(cart_item)
        else:
            return Response({'error':'That much product not available'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class CartItemsListview(APIView):
    serializer_class=serializers.CartItemSerializer
    queryset=models.CartItem.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request,format=None):
        try:
            user=self.request.user
            query=models.CartItem.objects.filter(cart__user=user)
            serializer = self.serializer_class(query, many=True)
            if serializer.data:
                return Response({"status":1,"data":serializer.data},status=status.HTTP_200_OK)
            else:
                return Response({"status":0,"Messtage":"No items in cart"})
        except:
            return Response({"Message":"somthing went wrong"})
        
class CartItemDelete(generics.DestroyAPIView):
    serializer_class = serializers.CartItemDeleteSerializer
    permission_classes = [IsAuthenticated]
    queryset = models.CartItem.objects.all()
   
        
class ProductDetailView(APIView):
    serializer_class=serializers.productDetailSerializer
    permission_classes = [IsAuthenticated]
   
    def get(self,request,pk,format=None):
        try:
            query = models.Product.objects.get(id=pk)
            serializer = self.serializer_class(query)
            if serializer.data:
                return Response({"status":1,"data":serializer.data},status=status.HTTP_200_OK)
        except models.Product.DoesNotExist:
            return Response({"status":0,"Message":"Product does not exist"})

class CategoryList(APIView):
    serializer_class = serializers.CategorySerializer
    permission_classes = [IsAuthenticated]

    def get(self,request,format=None):
        try:
            query = models.Category.objects.all()
            serializer = self.serializer_class(query,many=True)
            if serializer.data:
                return Response({"status":1,"data":serializer.data},status=status.HTTP_200_OK)
            else:
                return Response({"status":0,"Message":"No category"},status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"status":0,"Message":"TRY AGAIN"},status=status.HTTP_400_BAD_REQUEST)
    
class ListProductWithCategory(APIView):
    serializer_class = serializers.ProductSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, cat_id, format=None):
        try:
            category = models.Category.objects.get(pk=cat_id)
            products = models.Product.objects.filter(category=category)
            serializer = self.serializer_class(products, many=True)
            
            if serializer.data:
                for product_data in serializer.data:
                    product_data['product_id'] = product_data['id']
                return Response({"status": 1, "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"status": 0, "message": "No Products"}, status=status.HTTP_204_NO_CONTENT)
        except models.Category.DoesNotExist:
            return Response({"status": 0, "message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

class AddToPurchase(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = serializers.AddToPurchaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":1,"data":serializer.data,"message":"Added to Purchase"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

