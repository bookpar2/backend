from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, EmailVerification
from django.utils import timezone
from datetime import timedelta
import random
import string


class EmailVerificationSerializer(serializers.Serializer):
    school_email = serializers.EmailField()

    verification_type = serializers.ChoiceField(
        choices=['registration', 'password_reset'],
        default='registration'
    )

    def validate_school_email(self, value):
        domain = value.split('@')[1]
        if domain != 'tukorea.ac.kr':
            raise serializers.ValidationError("유효한 학교 이메일이 아닙니다.")
        return value


class VerifyCodeSerializer(serializers.Serializer):
    school_email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=10)

    def validate(self, data):
        try:
            verification = EmailVerification.objects.get(
                user_email=data['school_email'],
                verification_code=data['verification_code']
            )
            if not verification.is_valid():
                raise serializers.ValidationError("인증 코드가 만료되었습니다.")
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("유효하지 않은 인증 코드입니다.")
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    verification_code = serializers.CharField(max_length=10, write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('name', 'student_id', 'major', 'school_email', 'password', 'verification_code')

    def validate(self, data):
        try:
            verification = EmailVerification.objects.get(
                user_email=data['school_email'],
                verification_code=data['verification_code']
            )
            if not verification.is_valid():
                raise serializers.ValidationError({"verification_code": "인증 코드가 만료되었습니다."})
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError({"verification_code": "유효하지 않은 인증 코드입니다."})
        return data

    def create(self, validated_data):
        verification_code = validated_data.pop('verification_code')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.email_verified = True
        user.save()

        # 사용된 인증 코드 삭제
        EmailVerification.objects.filter(
            user_email=validated_data['school_email'],
            verification_code=verification_code
        ).delete()

        return user


class UserLoginSerializer(serializers.Serializer):
    school_email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        school_email = data.get('school_email')
        password = data.get('password')

        if school_email and password:
            # 이메일로 사용자 찾기
            try:
                user = User.objects.get(school_email=school_email)
            except User.DoesNotExist:
                raise serializers.ValidationError({"error": "잘못된 로그인 정보입니다."})

            # 비밀번호 확인
            if not user.check_password(password):
                raise serializers.ValidationError({"error": "잘못된 로그인 정보입니다."})

            # 이메일 인증 여부 확인
            if not user.email_verified:
                raise serializers.ValidationError({"error": "이메일 인증이 완료되지 않았습니다."})

            # 유저 정보 저장
            data['user'] = user
            return data

        raise serializers.ValidationError({"error": "이메일과 비밀번호를 모두 입력해주세요."})


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT 토큰에 추가 정보를 포함시키기 위한 커스텀 시리얼라이저"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # 토큰에 사용자 정보 추가
        token['name'] = user.name
        token['school_email'] = user.school_email
        token['student_id'] = user.student_id
        token['major'] = user.major

        return token


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    비밀번호 재설정을 위한 시리얼라이저
    """
    school_email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=10)
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        # 등록된 이메일인지 확인
        if not User.objects.filter(school_email=data['school_email']).exists():
            raise serializers.ValidationError({"school_email": "등록되지 않은 이메일입니다."})

        # 인증 코드 확인
        try:
            verification = EmailVerification.objects.get(
                user_email=data['school_email'],
                verification_code=data['verification_code'],
                verification_type='password_reset'
            )
            if not verification.is_valid():
                raise serializers.ValidationError({"verification_code": "인증 코드가 만료되었습니다."})
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError({"verification_code": "유효하지 않은 인증 코드입니다."})

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'school_email', 'major', 'name')