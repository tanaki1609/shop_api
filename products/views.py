from django.forms import model_to_dict
from django.http import JsonResponse
from products.models import Product

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from products.serializers import ProductSerializer


@api_view(['GET', 'POST'])
def product_list_create_api_view(request):
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
        # step 1: Receive data from request body
        title = request.data.get('title')
        text = request.data.get('text')
        price = request.data.get('price')
        is_active = request.data.get('is_active')
        category_id = request.data.get('category_id')
        tags = request.data.get('tags')

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
        product.title = request.data.get('title')
        product.text = request.data.get('text')
        product.price = request.data.get('price')
        product.is_active = request.data.get('is_active')
        product.category_id = request.data.get('category_id')
        product.tags.set(request.data.get('tags'))
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
