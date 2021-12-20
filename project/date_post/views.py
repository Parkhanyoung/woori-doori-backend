from user.models import Profile
from couple_network.models import CoupleNet
from .serializers import DayCommentDetailSerializer, PlaceSerializer,  \
                         PostDetailSerializer, DayCommentCreateSerializer, \
                         DatePostCommentSerializer, PostCreateSerializer, \
                         PostImageSerializer
from .helpers import modify_img_for_multiple_imgs

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q

import re


class PlaceAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        print(request.user)
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

    def patch(self, request):
        me = get_object_or_404(Profile, user=request.user)
        couple = get_object_or_404(CoupleNet, members=me)
        placepk = request.data.get('placepk')
        if not placepk:
            msg = {'Err': 'placepk를 포함하여 요청을 보내주세요.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        place = couple.places.all().filter(pk=placepk)
        if not place:
            msg = {'Err': '해당 커플의 place가 아니거나 존재하지 않는 place입니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        serializer = PlaceSerializer(place[0], data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        me = get_object_or_404(Profile, user=request.user)
        couple = get_object_or_404(CoupleNet, members=me)
        placepk = request.data.get('placepk')
        if not placepk:
            msg = {'Err': 'placepk를 포함하여 요청을 보내주세요.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        place = couple.places.all().filter(pk=placepk)
        if not place:
            msg = {'Err': '해당 커플의 place가 아니거나 존재하지 않는 place입니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        placename = place[0].name
        place[0].delete()
        msg = {'Succ': f'{placename}이(가) 성공적으로 삭제되었습니다.'}
        return Response(msg, status=status.HTTP_204_NO_CONTENT)


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
        serializer = PostDetailSerializer(posts, many=True,
                                          context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PostCreateSerializer(data=request.data)
        if serializer.is_valid():
            me = get_object_or_404(Profile, user=request.user)
            couple = get_object_or_404(CoupleNet, members=me)
            place = serializer.validated_data.get('place')
            if not place.couple == couple:
                msg = {'Err': '요청 사용자 커플의 place가 아닙니다.'}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(author=me, couple=couple)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        me = get_object_or_404(Profile, user=request.user)
        couple = get_object_or_404(CoupleNet, members=me)
        postpk = request.data.get('postpk')
        if not postpk:
            msg = {'Err': 'postpk를 body에 담아 요청을 보내주세요'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        post = couple.posts.all().filter(pk=postpk)
        if not post:
            msg = {'Err': '요청 사용자 커플의 post가 아니거나 없는 post입니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        serializer = PostCreateSerializer(post[0], data=request.data,
                                          partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
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
        serializer = DayCommentDetailSerializer(today_comments, many=True,
                                                context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        when = request.data.get('when')
        if not when:
            msg = {'Err': 'when을 포함하여 요청을 보내주세요'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        me = get_object_or_404(Profile, user=request.user)
        couple = get_object_or_404(CoupleNet, members=me)
        
        if couple.daycomments.all().filter(Q(when=when) & Q(author=me)):
            msg = {'Err': '이미 해당 날짜의 daycomment를 작성했습니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        serializer = DayCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
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
            serializer = DatePostCommentSerializer(comments, many=True,
                                                   context={'request':request})
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DatePostCommentSerializer(data=request.data,
                                               context={'request':request})
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


class PostImageAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        me = get_object_or_404(Profile, user=request.user)
        couple = get_object_or_404(CoupleNet, members=me)

        post_pk = request.data.get('date_post')
        if not post_pk:
            msg = {'Err': 'date_post를 포함하여 요청을 보내주세요.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        
        post = couple.posts.all().filter(pk=post_pk)
        if not post.exists():
            msg = {'Err': '해당 게시글은 다른 커플의 게시글입니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        if post[0].images.all():
            msg = {'Err': '해당 게시글에 이미 이미지가 있습니다. update url을 이용하세요.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        try:
            images = dict((request.data).lists())['images']
        except:
            msg = {'Err': 'images를 포함하여 요청을 보내주세요.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        if not (1 <= len(images) <= 3 and images[0] != ''):
            msg = {'Err': '사진을 1개 이상 3개 이하로 첨부해주세요.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            i = 0
            for img in images:
                i += 1
                modified_img = modify_img_for_multiple_imgs(post_pk, img)
                serializer = PostImageSerializer(data=modified_img)
                success = True
                if serializer.is_valid():
                    img.name = f'{post_pk}-{i}.png'
                    serializer.save(uploader=me)
                else:
                    success = False
                    transaction.set_rollback(True)
                    break

        if success:
            msg = {'Succ': f'{len(images)}개의 사진이 성공적으로 저장되었습니다.'}
            return Response(msg, status=status.HTTP_201_CREATED)
        else:
            msg = {'Err': '잘못된 형식의 사진이 포함되어 있습니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        