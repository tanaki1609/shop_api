from rest_framework import serializers
from products.models import Product, Category, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = 'id name'.split()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = 'id name'.split()


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)
    tags = TagSerializer(many=True)
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = 'id reviews category category_name tags tag_list title price created'.split()
        depth = 1

    def get_category_name(self, product):
        return product.category.name if product.category else None
