from rest_framework import serializers

from django.contrib.auth import get_user_model, authenticate

from .models import Profile


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 6}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
            instance.save()
        return instance


    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        if username:
            if username.isnumeric():
                msg = {"Err": "username에 문자나 기호를 적어도 하나 포함시켜야 합니다."}
                raise serializers.ValidationError(msg, code='username format')
        if password:
            if password.isnumeric():
                msg = {"Err": "password에 문자나 기호를 적어도 하나 포함시켜야 합니다."}
                raise serializers.ValidationError(msg, code='password format')
        return attrs


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password,
        )

        if not user:
            msg = {'authentication': 'Invalid credential'}
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs


class ProfileRetrieveSerializer(serializers.ModelSerializer):
    profile_img = serializers.SerializerMethodField()

    def get_profile_img(self, obj):
        request = self.context.get('request')
        image_url = obj.profile_img.url
        return request.build_absolute_uri(image_url)

    class Meta:
        model = Profile
        fields = ['id', 'nickname', 'gender', 'profile_img', 'id_code']
        read_only_fields = ['id', 'id_code']


class ProfileSerializer(serializers.ModelSerializer):
    profile_img = serializers.ImageField()

    class Meta:
        model = Profile
        fields = ['id', 'nickname', 'gender', 'profile_img', 'id_code']
        read_only_fields = ['id', 'id_code']
