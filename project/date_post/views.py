from user.models import Profile
from couple_network.models import CoupleNet
from .models import Place, DayComment
from .serializers import PlaceSerializer, PostCreateSerializer, \
                         PostDetailSerializer, DayCommentCreateSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404


class PlaceAPIView(APIView):

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
            places = couple.places.all().filter(category=value_query
                                             ).order_by('-visit_count')
        serializer = PlaceSerializer(places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    

    def post(self, request):
        me = get_object_or_404(Profile, user=request.user)
        couple = get_object_or_404(CoupleNet, members=me)
        serializer = PlaceSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            latitude = serializer.validated_data.get('latitude')
            place = Place.objects.filter(name=name).filter(latitude=latitude)
            if place:
                place[0].visit_count += 1
                place[0].save()
                msg = {'Succ': '기존 장소의 방문 횟수가 1 증가했습니다.'}
                return Response(msg, status=status.HTTP_200_OK)
            else:
                serializer.save(couple=couple)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)


class DatePostAPIView(APIView):

    def get(self, request):
        me = get_object_or_404(Profile, user=request.user)
        couple = get_object_or_404(CoupleNet, members=me)
        filter_query = request.query_params.get('filter')
        value_query = request.query_params.get('value')
        if not (filter_query and value_query):
            msg = {'Err': 'filter 및 value 쿼리스트링이 모두 필요합니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        elif not (filter_query == 'placepk' or 
                  filter_query == 'when' or 
                  filter_query == 'postpk'):
            msg = {'Err': 'filter 쿼리스트링 값이 올바르지 않습니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        elif filter_query == 'placepk':
            posts = couple.posts.all().filter(place__pk=value_query)
        elif filter_query == 'when':
            posts = couple.posts.all().filter(when=value_query)
        elif filter_query == 'postpk':
            posts = couple.posts.all().filter(pk=value_query)
        serializer = PostDetailSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PostCreateSerializer(data=request.data)
        if serializer.is_valid():
            me = get_object_or_404(Profile, user=request.user)
            couple = get_object_or_404(CoupleNet, members=me)
            serializer.save(author=me, couple=couple)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DayCommentAPIView(APIView):

    def post(self, request):
        serializer = DayCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            me = get_object_or_404(Profile, user=request.user)
            couple = get_object_or_404(CoupleNet, members=me)
            serializer.save(author=me, couple=couple)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
