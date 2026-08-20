from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator
from .models import PictureAI
from .serializers import PictureAISerializer  # Đảm bảo bạn đã tạo PictureAISerializer trong serializers.py

@api_view(['GET'])
def index(request):
    # Sắp xếp theo ID hoặc ngày tạo giảm dần để phân trang không bị trùng lặp dữ liệu
    pic_list = PictureAI.objects.all().order_by('-created_at')
    
    # Phân trang: 8 phần tử một trang giống logic cũ của bạn
    paginator = Paginator(pic_list, 8)
    page = request.GET.get('page', 1)  # Mặc định lấy trang 1 nếu không truyền tham số
    
    current_page_data = paginator.get_page(page)
    
    # Serialize danh sách các bức ảnh của trang hiện tại
    serializer = PictureAISerializer(current_page_data.object_list, many=True)
    
    # Trả về cấu trúc JSON đồng bộ với API bên posts để Laravel dễ xử lý
    return Response({
        'data': serializer.data,
        'current_page': current_page_data.number,
        'last_page': paginator.num_pages,
        'total': paginator.count
    })