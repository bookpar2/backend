from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from chat.models import ChatRoom, Message
from users.models import User
from book.models import Book

#채팅방 생성 API
@api_view(['POST'])
def create_chatroom(request):
    buyer_id = request.data.get('buyer_id')
    book_id = request.data.get('book_id')

    try:
        buyer = User.objects.get(id=buyer_id)
        book = Book.objects.get(id=book_id)
        seller = book.seller

        #기존 채팅방 확인
        chatroom, created = ChatRoom.objects.get_or_create(
            buyer=buyer,
            book=book,
            seller=seller
        )

        return Response({
            "chatroom_id": chatroom.id,
            "message": "채팅방이 생성되었습니다." if created else "기존 채팅방이 있습니다."
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"error": "구매자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    except Book.DoesNotExist:
        return Response({"error": "책 정보를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

#특정 채팅방 내용 조회 API
@api_view(['GET'])
def get_chatroom_messages(request, chatroom_id):
    #현재 로그인한 사용자의 ID 가져오기
    current_user_id = request.GET.get('user_id')

    try:
        #현재 사용자 및 채팅방 조회
        current_user = User.objects.get(id=current_user_id)
        chatroom = ChatRoom.objects.get(id=chatroom_id)

        #상대방 정보 구하기 (구매자인지 판매자인지 판별)
        if chatroom.buyer == current_user:
            opponent = chatroom.book.seller
        elif chatroom.book.seller == current_user:
            opponent = chatroom.buyer
        else:
            return Response({"error": "채팅방에 접근 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        #채팅방 내 메시지 조회
        messages = Message.objects.filter(chatRoom=chatroom).order_by('time')

        #응답 형식 만들기
        message_list = [{
            "sender": "나" if msg.sender == current_user else opponent.name,
            "content": msg.content,
            "time": msg.time
        } for msg in messages]

        return Response({
            "chatroom_id": chatroom.id,
            "opponent_name": opponent.name,
            "messages": message_list
        }, status=status.HTTP_200_OK)

    except ChatRoom.DoesNotExist:
        return Response({"error": "채팅방을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    except User.DoesNotExist:
        return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


# 채팅방 목록 조회 API
@api_view(['GET'])
def get_chatrooms(request):
    """
    사용자가 참여한 모든 채팅방을 조회하는 API
    """
    user_id = request.GET.get('user_id')

    if not user_id:
        return Response({"error": "user_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)

        #사용자가 구매자 or 판매자로 참여한 채팅방 조회
        chatrooms = ChatRoom.objects.filter(
            buyer=user
        ) | ChatRoom.objects.filter(seller=user)

        chatrooms = chatrooms.order_by('-updated_at')  # 최신 채팅방 순서대로 정렬

        chatroom_list = []
        for chatroom in chatrooms:
            opponent = chatroom.seller if chatroom.buyer == user else chatroom.buyer  # 상대방 이름 찾기

            chatroom_list.append({
                "chatroom_id": chatroom.id,
                "opponent_name": opponent.username,
                "book_title": chatroom.book.title,
                "last_message": chatroom.last_message or "",
                "updated_at": chatroom.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        return Response({"chatrooms": chatroom_list}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


def websocket_test(request):

    return render(request, "test.html")