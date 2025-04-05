from rest_framework import serializers
from .models import Workshop, WorkshopImage360, WorkshopRating

class WorkshopImage360Serializer(serializers.ModelSerializer):
    class Meta:
        model = WorkshopImage360
        fields = ['id', 'image_360']

class WorkshopRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkshopRating
        fields = ['id', 'rating', 'created_at']

class WorkshopSerializer(serializers.ModelSerializer):
    images_360 = WorkshopImage360Serializer(many=True, read_only=True)
    ratings = WorkshopRatingSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Workshop
        fields = ['id', 'user', 'name', 'description', 'img', 'address', 'created_at', 'updated_at', 'images_360', 'ratings', 'average_rating', 'is_owner']

    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if ratings.exists():
            return round(sum(rating.rating for rating in ratings) / ratings.count(), 1)
        return 0

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False