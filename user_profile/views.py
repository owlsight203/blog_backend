from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Profile
from .serializers import ProfileSerializer  # Đảm bảo bạn đã import đúng tên class từ serializers.py của app này

@api_view(['GET'])
def profilepage(request):
    # Kiểm tra xem user có đăng nhập qua session/token của Django hay chưa
    if not request.user.is_authenticated:
        default_user = User.objects.first()
        if not default_user:
            return Response({'error': 'Không có user nào tồn tại trong hệ thống.'}, status=404)
            
        try:
            default_profile = Profile.objects.get(user=default_user)
            serializer = ProfileSerializer(default_profile)
            return Response({
                'anonymous': True,
                'profile': serializer.data
            })
        except Profile.DoesNotExist:
            return Response({'error': 'Profile mặc định không tồn tại.'}, status=404)
            
    # Trường hợp đã xác thực thành công
    try:
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response({
            'anonymous': False,
            'profile': serializer.data
        })
    except Profile.DoesNotExist:
        return Response({'error': 'Profile của user này không tồn tại.'}, status=404)