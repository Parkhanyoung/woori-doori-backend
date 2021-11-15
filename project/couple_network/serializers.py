from .models import CoupleRequest, CoupleNet

from rest_framework import serializers

from user.serializers import ProfileSerializer


class CoupleRequestSerializer(serializers.ModelSerializer):
    requestor = ProfileSerializer(read_only=True)
    responsor = ProfileSerializer(read_only=True)

    class Meta:
        model = CoupleRequest
        fields = ['id', 'created_at', 'requestor', 'responsor']
        read_only_fields = ('id',)


class CoupleNetSerializer(serializers.ModelSerializer):
    members = ProfileSerializer(read_only=True, many=True)

    class Meta:
        model = CoupleNet
        fields = ['id', 'created_at', 'members']
        read_only_fields = ('id', 'members')
