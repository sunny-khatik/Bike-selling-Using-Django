from rest_framework import serializers
from .models import Prod


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prod
        fields = ('category', 'slug', 'name', 'image', "description")
