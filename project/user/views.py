from .serializers import UserSerializer, AuthTokenSerializer, \
                         ProfileSerializer

from .models import Profile

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

import uuid


class PublicUserAPIView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ProfileAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = Profile.objects.filter(user=request.user)
        if not profile:
            msg = f'{request.user.username}님은 아직 프로필을 만들지 않았습니다.'
            context = {}
            context['Err'] = msg
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = ProfileSerializer(profile[0])
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if Profile.objects.filter(user=request.user):
            msg = f'{request.user.username}님은 이미 프로필이 있습니다.'
            context = {}
            context['Err'] = msg
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        ext = request.FILES['profile_img'].name.split('.')[-1]
        request.FILES['profile_img'].name = request.user.username + '.' + ext
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            id_code = str(uuid.uuid4())[:18]
            serializer.save(user=request.user, id_code=id_code)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
