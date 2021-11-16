from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import CoupleRequest, CoupleNet
from .serializers import CoupleRequestSerializer, CoupleNetSerializer

from user.models import Profile

from django.db.models import Q
from django.shortcuts import get_object_or_404


class CoupleRequestAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        my_profile = get_object_or_404(Profile, user=request.user)
        request_sent = CoupleRequest.objects.filter(requestor=my_profile)
        request_receive = CoupleRequest.objects.filter(responsor=my_profile)
        if request_sent:
            serializer = CoupleRequestSerializer(request_sent[0])
            context = {}
            context['data'] = serializer.data
            context['receiver'] = 'not_me'
            return Response(context, status=status.HTTP_200_OK)
        elif request_receive:
            serializer = CoupleRequestSerializer(request_receive[0])
            context = {}
            context['data'] = serializer.data
            context['receiver'] = 'me'
            return Response(context, status=status.HTTP_200_OK)
        Err = '받거나 보낸 요청이 없습니다.'
        return Response({'Err': Err}, status=status.HTTP_404_NOT_FOUND)

    def check_myself(self):
        me = get_object_or_404(Profile, user=self.request.user)
        result = {'ok': True, 'user': me}
        if CoupleRequest.objects.filter(requestor=me):
            result['ok'] = False
            result['Err'] = '이미 요청을 보낸 사용자는 요청을 보낼 수 없습니다.'
        elif CoupleRequest.objects.filter(responsor=me):
            result['ok'] = False
            result['Err'] = '이미 요청을 받은 사용자는 요청을 보낼 수 없습니다.'
        elif CoupleNet.objects.filter(members=me):
            result['ok'] = False
            result['Err'] = '이미 커플인 사용자는 요청을 보낼 수 없습니다.'
        return result

    def check_partner(self):
        id_code = self.request.data.get('id_code')
        partner = Profile.objects.filter(id_code=id_code)
        result = {'ok': True, 'msg': '요청에 성공했습니다.', 'user': partner}
        if not id_code:
            result['ok'] = False
            result['Err'] = 'id_code를 포함해서 요청을 보내주세요.'
        elif not partner:
            result['ok'] = False
            result['Err'] = '유효하지 않은 id_code입니다.'
        elif CoupleRequest.objects.filter(Q(responsor=partner[0]) |
                                          Q(requestor=partner[0])):
            result['ok'] = False
            result['Err'] = '이미 요청을 보내거나 받은 사용자에게 요청을 보낼 수 없습니다.'
        elif CoupleNet.objects.filter(members=partner[0]):
            result['ok'] = False
            result['Err'] = '이미 커플인 유저에게는 요청을 보낼 수 없습니다.'
        return result

    def post(self, request):
        myself = self.check_myself()
        if myself['ok']:
            partner = self.check_partner()
            if partner['ok']:
                CoupleRequest.objects.create(
                    requestor=myself['user'],
                    responsor=partner['user'][0]
                )
                return Response({'Succ': partner['msg']},
                                status=status.HTTP_201_CREATED)
            return Response({'Err': partner['Err']},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Err': myself['Err']},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        my_request = CoupleRequest.objects.filter(Q(requestor=profile) |
                                                  Q(responsor=profile))
        if my_request:
            my_request[0].delete()
            msg = {'succ': '요청이 삭제되었습니다.'}
            return Response(msg, status=status.HTTP_204_NO_CONTENT)
        else:
            msg = {'Err': '사용자에게 온 요청이 없습니다.'}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)


class CoupleNetworkAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        my_request = CoupleRequest.objects.filter(responsor=profile)
        if my_request:
            if CoupleNet.objects.filter(members=profile):
                my_request[0].delete()
                msg = {'Err': '이미 커플에 속해있는 사용자입니다.'}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            partner = my_request[0].requestor
            couple = CoupleNet()
            couple.save()
            couple.members.add(profile.pk, partner.pk)
            profile.is_alone = False
            partner.is_alone = False
            profile.save()
            partner.save()
            my_request[0].delete()
            serializer = CoupleNetSerializer(couple)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            msg = {'Err': '사용자에게 온 요청이 없습니다.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        me = get_object_or_404(Profile, user=request.user)
        couple = get_object_or_404(CoupleNet, members=me)
        serializer = CoupleNetSerializer(couple, data=request.data,
                                         partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        my_network = CoupleNet.objects.filter(members=profile)
        if my_network:
            my_network[0].delete()
            msg = {'Succ': '성공적으로 삭제되었습니다.'}
            return Response(msg, status=status.HTTP_204_NO_CONTENT)
        msg = {'Err': '삭제할 couple network가 없습니다'}
        return Response(msg, status=status.HTTP_404_NOT_FOUND)
