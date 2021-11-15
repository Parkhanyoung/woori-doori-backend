from user.models import Profile
from couple_network.models import CoupleNet
from .serializers import DayCommentDetailSerializer, PlaceSerializer,  \
                         PostDetailSerializer, DayCommentCreateSerializer, \
                         DatePostCommentSerializer, PostCreateSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

import re


class PlaceAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        me = get_object_or_404(Profile, user=request.user)
        couple = get_object_or_404(CoupleNet, members=me)
        filter_query = request.query_params.get('filter')
        value_query = request.query_params.get('value')
        if not filter_query:
            msg = {'Err': 'filter 쿼리스트링을 포함해야 합니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        elif not (filter_query == 'all' or filter_query == 'category'):
            msg = {'Err': '쿼리스트링 값이 올바르지 않습니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        elif filter_query == 'all':
            places = couple.places.all()
        elif filter_query == 'category':
            if not value_query:
                msg = {'Err': 'value 쿼리스트링을 포함해야 합니다.'}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            places = couple.places.all().filter(category=value_query).order_by(
                                                '-visit_count')
        serializer = PlaceSerializer(places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        me = get_object_or_404(Profile, user=request.user)
        couple = get_object_or_404(CoupleNet, members=me)
        serializer = PlaceSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            latitude = serializer.validated_data.get('latitude')
            place = couple.places.all().filter(name=name).filter(
                                               latitude=latitude)
            if place:
                place[0].visit_count += 1
                place[0].save()
                msg = {'Succ': '기존 장소의 방문 횟수가 1 증가했습니다.'}
                return Response(msg, status=status.HTTP_200_OK)
            else:
                serializer.save(couple=couple)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DatePostAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        me = get_object_or_404(Profile, user=request.user)
        couple = get_object_or_404(CoupleNet, members=me)
        filter_query = request.query_params.get('filter')
        value_query = request.query_params.get('value')
        date_type = re.compile('\d{4}-\d{2}-\d{2}') # noqa
        if not (filter_query and value_query):
            msg = {'Err': 'filter 및 value 쿼리스트링이 모두 필요합니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        elif not (filter_query == 'placepk' or
                  filter_query == 'when' or
                  filter_query == 'postpk'):
            msg = {'Err': 'filter 쿼리스트링 값이 올바르지 않습니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        elif filter_query == 'placepk':
            if not value_query.isdecimal():
                msg = {'Err': 'value 쿼리스트링이 Int형이어야 합니다.'}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            posts = couple.posts.all().filter(place__pk=value_query)
        elif filter_query == 'when':
            if not date_type.match(value_query):
                msg = {'Err': 'value 쿼리스트링이 YYYY-MM-DD의 형태여야 합니다.'}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            posts = couple.posts.all().filter(when=value_query)
        elif filter_query == 'postpk':
            if not value_query.isdecimal():
                msg = {'msg': 'value 쿼리스트링이 Int형이어야 합니다.'}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            posts = couple.posts.all().filter(pk=value_query)
        serializer = PostDetailSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PostCreateSerializer(data=request.data)
        if serializer.is_valid():
            me = get_object_or_404(Profile, user=request.user)
            couple = get_object_or_404(CoupleNet, members=me)
            place = serializer.validated_data.get('place')
            if not place.couple == couple:
                msg = {'Err': '해당 커플의 place가 아닙니다.'}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(author=me, couple=couple)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DayCommentAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        me = get_object_or_404(Profile, user=request.user)
        couple = get_object_or_404(CoupleNet, members=me)
        filter_query = request.query_params.get('filter')
        value_query = request.query_params.get('value')
        date_type = re.compile('\d{4}-\d{2}-\d{2}') # noqa
        if not (filter_query == 'when' and value_query):
            msg = {'Err': 'filter(=when) 및 value 쿼리스트링이 모두 필요합니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        elif not date_type.match(value_query):
            msg = {'Err': 'value 쿼리스트링은 YYYY-MM-DD의 형태여야 합니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        today_comments = couple.daycomments.all().filter(when=value_query)
        serializer = DayCommentDetailSerializer(today_comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DayCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            me = get_object_or_404(Profile, user=request.user)
            couple = get_object_or_404(CoupleNet, members=me)
            serializer.save(author=me, couple=couple)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostCommentAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        me = get_object_or_404(Profile, user=request.user)
        couple = get_object_or_404(CoupleNet, members=me)
        filter_query = request.query_params.get('filter')
        value_query = request.query_params.get('value')
        if not value_query.isdecimal():
            msg = {'Err': 'value 쿼리스트링 값은 정수 형태여야 합니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        posts = couple.posts.all().filter(pk=value_query)
        if not (filter_query == 'postpk' and value_query):
            msg = {'Err': 'filter(=postpk) 및 value 쿼리스트링이 모두 필요합니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        elif not posts:
            msg = {'Err': '해당 게시글은 다른 커플의 게시글이거나 없는 게시글입니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        else:
            comments = posts[0].comments.all()
            serializer = DatePostCommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DatePostCommentSerializer(data=request.data)
        if serializer.is_valid():
            me = get_object_or_404(Profile, user=request.user)
            couple = get_object_or_404(CoupleNet, members=me)
            post = serializer.validated_data.get('date_post')
            if not post.couple == couple:
                msg = {'Err': '해당 게시글은 다른 커플의 게시글입니다.'}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(author=me)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
