from collections import OrderedDict

from django.forms import model_to_dict
from django.http import JsonResponse
from products.models import Product, Category, Tag

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from products.serializers import (ProductSerializer,
                                  ProductValidateSerializer,
                                  CategorySerializer,
                                  TagSerializer)

from users.permissions import IsSuperUser
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'id'


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('total', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class CategoryListAPIView(ListCreateAPIView):
    queryset = Category.objects.all()  # List objects received from DB
    serializer_class = CategorySerializer  # Serializer inherited by ModelSerializer
    pagination_class = CustomPagination


class CategoryDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListCreateAPIView(ListCreateAPIView):
    queryset = (Product.objects.select_related('category')
                .prefetch_related('tags', 'reviews').all())
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        # step 0: Validation of data (Existing, Typing, Extra)
        serializer = ProductValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)

        # step 1: Receive data from request body
        title = serializer.validated_data.get('title')  # new title
        text = serializer.validated_data.get('text')  # None
        price = serializer.validated_data.get('price')  # 1.1
        is_active = serializer.validated_data.get('is_active')  # None
        category_id = serializer.validated_data.get('category_id')
        tags = serializer.validated_data.get('tags')

        # step 2: Create product by received data
        product = Product.objects.create(
            title=title,
            text=text,
            price=price,
            is_active=is_active,
            category_id=category_id,
        )
        product.tags.set(tags)
        product.save()

        # step 3: Return response with data and status
        return Response(data={'product_id': product.id},
                        status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([IsSuperUser])
def product_list_create_api_view(request):
    print(request.user)
    if request.method == 'GET':
        search = request.query_params.get('search', '')
        # step 1: collect data (QuerySet)
        products = (Product.objects.select_related('category')
                    .prefetch_related('tags', 'reviews').filter(title__icontains=search))

        # step 2: reformat data (QueryDict)
        data = ProductSerializer(instance=products, many=True).data

        # step 3: return response
        return Response(data=data)
    elif request.method == 'POST':
        # step 0: Validation of data (Existing, Typing, Extra)
        serializer = ProductValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)

        # step 1: Receive data from request body
        title = serializer.validated_data.get('title')  # new title
        text = serializer.validated_data.get('text')  # None
        price = serializer.validated_data.get('price')  # 1.1
        is_active = serializer.validated_data.get('is_active')  # None
        category_id = serializer.validated_data.get('category_id')
        tags = serializer.validated_data.get('tags')

        # step 2: Create product by received data
        product = Product.objects.create(
            title=title,
            text=text,
            price=price,
            is_active=is_active,
            category_id=category_id,
        )
        product.tags.set(tags)
        product.save()

        # step 3: Return response with data and status
        return Response(data={'product_id': product.id},
                        status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail_api_view(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND,
                        data={'detail': 'Product not found!'})
    if request.method == 'GET':
        data = ProductSerializer(product).data
        return Response(data=data)
    elif request.method == 'PUT':
        serializer = ProductValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product.title = serializer.validated_data.get('title')
        product.text = serializer.validated_data.get('text')
        product.price = serializer.validated_data.get('price')
        product.is_active = serializer.validated_data.get('is_active')
        product.category_id = serializer.validated_data.get('category_id')
        product.tags.set(serializer.validated_data.get('tags'))
        product.save()
        return Response(data=ProductSerializer(product).data,
                        status=status.HTTP_201_CREATED)
    else:
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def product_list_view(request):
    products = Product.objects.all()
    list_ = []
    for i in products:
        list_.append(model_to_dict(instance=i))
    return JsonResponse(data=list_, safe=False)
