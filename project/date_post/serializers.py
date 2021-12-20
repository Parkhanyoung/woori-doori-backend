from rest_framework import serializers

from .models import Place, DatePost, DayComment, DatePostComment, PostImage

from user.serializers import ProfileRetrieveSerializer


class PlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Place
        fields = ['id', 'category', 'name', 'latitude', 'longitude',
                  'address', 'visit_count']
        read_only_fields = ['id', 'visit_count']


class PostDetailSerializer(serializers.ModelSerializer):
    place = PlaceSerializer(read_only=True)
    author = ProfileRetrieveSerializer(read_only=True)
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        request = self.context.get('request')
        image_queryset = obj.images.all()
        return PostImageRetrieveSerializer(
            image_queryset,
            many=True, 
            context={'request':request}
            ).data

    class Meta:
        model = DatePost
        fields = ['id', 'title', 'content', 'score', 'when',
                  'author', 'place', 'images']
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
    author = ProfileRetrieveSerializer(read_only=True)

    class Meta:
        model = DayComment
        fields = ['id', 'content', 'when', 'author']
        read_only_fields = ('id',)


class DatePostCommentSerializer(serializers.ModelSerializer):
    author = ProfileRetrieveSerializer(read_only=True)
    date_post = serializers.PrimaryKeyRelatedField(
                queryset=DatePost.objects.all())

    class Meta:
        model = DatePostComment
        fields = ['id', 'author', 'content', 'date_post']
        read_only_fields = ('id',)


class PostImageSerializer(serializers.ModelSerializer):
    content = serializers.ImageField(use_url=True)
    date_post = serializers.PrimaryKeyRelatedField(
                queryset=DatePost.objects.all())

    class Meta:
        model = PostImage
        fields = ['id', 'content', 'date_post']
        read_only_fields = ('id',)


class PostImageRetrieveSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        request = self.context.get('request')
        image_url = obj.content.url
        return request.build_absolute_uri(image_url)
    
    class Meta:
        model = PostImage
        fields = ['id', 'content']
        read_only_fields = ('id',)
