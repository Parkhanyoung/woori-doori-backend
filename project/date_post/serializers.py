from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

from .models import Place, DatePost, DayComment, DatePostComment

from user.serializers import ProfileSerializer


class PlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Place
        fields = ['id', 'category', 'name', 'latitude', 'longitude',
                  'address', 'visit_count']
        read_only_fields = ['id', 'visit_count']


class PostDetailSerializer(serializers.ModelSerializer):
    place = PlaceSerializer(read_only=True)
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = DatePost
        fields = ['id', 'title','content', 'score', 'when', 'author', 'place']
        read_only_fields = ('id',)

class PostCreateSerializer(serializers.ModelSerializer):
    place = serializers.PrimaryKeyRelatedField(queryset=Place.objects.all())

    def validate(self, attrs):
        score = attrs.get('score')
        if not (score > 0 and score < 6):
            msg = {'Err': 'score는 1과 5 사이의 정수 중 하나여야 합니다.'}
            raise serializers.ValidationError(msg, code='format')
        return attrs

    class Meta:
        model = DatePost
        fields = ['id', 'title', 'content', 'score', 'order', 'when', 'place']
        read_only_fields = ('id',)


class DayCommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DayComment
        fields = ['id', 'content', 'when']
        read_only_fields = ('id',)


class DayCommentDetailSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = DayComment
        fields = ['id', 'content', 'when', 'author']
        read_only_fields = ('id',)


class DatePostCommentSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    date_post = serializers.PrimaryKeyRelatedField(
                queryset=DatePost.objects.all())

    class Meta:
        model = DatePostComment
        fields = ['id', 'author', 'content', 'date_post']
        read_only_fields = ('id',)