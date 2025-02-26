from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.conf import settings
from .models import User, EmailVerification
from .serializers import (
    EmailVerificationSerializer,
    VerifyCodeSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserLoginSerializer,
    PasswordResetConfirmSerializer
)
from django.utils import timezone
from datetime import timedelta
import random
import string



def generate_verification_code():
    """6자리 알파벳 + 숫자 조합 인증 코드 생성"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))


class SendVerificationEmailView(APIView):
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['school_email']
            verification_type = serializer.validated_data.get('verification_type', 'registration')

            # 회원가입의 경우 이미 가입된 이메일인지 확인
            if verification_type == 'registration' and User.objects.filter(school_email=email).exists():
                return Response(
                    {"error": "이미 가입된 이메일입니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 비밀번호 재설정의 경우 가입된 이메일이 아니면 오류
            if verification_type == 'password_reset' and not User.objects.filter(school_email=email).exists():
                return Response(
                    {"error": "등록되지 않은 이메일입니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 이전에 발급된 같은 유형의 코드가 있으면 삭제
            EmailVerification.objects.filter(
                user_email=email,
                verification_type=verification_type
            ).delete()

            # 새 인증 코드 생성
            verification_code = generate_verification_code()
            expires_at = timezone.now() + timedelta(minutes=10)  # 10분 유효

            # DB에 저장
            EmailVerification.objects.create(
                user_email=email,
                verification_code=verification_code,
                expires_at=expires_at,
                verification_type=verification_type
            )

            # 이메일 제목과 내용 설정
            if verification_type == 'registration':
                subject = '[TU Korea] 회원가입 이메일 인증 코드'
                message = f'회원가입을 위한 인증 코드는 {verification_code} 입니다. 이 코드는 10분간 유효합니다.'
            else:  # password_reset
                subject = '[TU Korea] 비밀번호 변경 인증 코드'
                message = f'비밀번호 변경을 위한 인증 코드는 {verification_code} 입니다. 이 코드는 10분간 유효합니다.'

            # 이메일 발송
            sender_email = settings.EMAIL_HOST_USER
            recipient_list = [email]

            try:
                send_mail(subject, message, sender_email, recipient_list)
                return Response(
                    {"message": "인증 이메일이 발송되었습니다."},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"error": f"이메일 발송 중 오류가 발생했습니다: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailCodeView(APIView):
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"message": "인증 코드가 확인되었습니다."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)

            # 응답 데이터 구성
            response_data = UserSerializer(user).data

            # 토큰 데이터 추가
            token_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return Response(
                {**response_data, **token_data},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)

            # 커스텀 클레임 추가
            refresh['name'] = user.name
            refresh['school_email'] = user.school_email

            # 응답 데이터 구성
            response_data = UserSerializer(user).data

            # 토큰 데이터 추가
            token_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return Response(
                {**response_data, **token_data},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({"error": "리프레시 토큰이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

            # 리프레시 토큰 블랙리스트에 추가하여 무효화
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "로그아웃 되었습니다."}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmView(APIView):
    """
    비밀번호 재설정 API
    """

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['school_email']
            verification_code = serializer.validated_data['verification_code']
            new_password = serializer.validated_data['new_password']

            # 사용자 찾기
            try:
                user = User.objects.get(school_email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "등록되지 않은 이메일입니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 비밀번호 변경
            user.set_password(new_password)
            user.save()

            # 사용된 인증 코드 삭제
            EmailVerification.objects.filter(
                user_email=email,
                verification_code=verification_code,
                verification_type='password_reset'
            ).delete()

            # 새 토큰 발급
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "비밀번호가 성공적으로 변경되었습니다.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)