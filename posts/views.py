import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

# Đảm bảo các model và serializer đã được import đúng cấu trúc thư mục của bạn
from .models import Post, Comment 
from .serializers import PostSerializer, CommentSerializer


from django.db.models import Q
from django.shortcuts import get_object_or_404

# ==================== 1. CÁC API HỆ THỐNG ====================


@api_view(['GET'])
def index(request):
    user_id = request.GET.get('user_id')
    
    if user_id:
        # Đã đăng nhập: thấy Public + Private của chính mình
        posts = Post.objects.filter(
            Q(status='public') | Q(status='private', author_user_id=user_id)
        ).distinct().order_by('-created_at')
    else:
        # Chưa đăng nhập: chỉ thấy Public
        posts = Post.objects.filter(status='public').order_by('-created_at')
    
    paginator = Paginator(posts, 8)
    page = request.GET.get('page', 1)
    current_page = paginator.get_page(page)
    
    return Response({
        'data': PostSerializer(current_page.object_list, many=True).data,
        'current_page': current_page.number,
        'last_page': paginator.num_pages,
        'total': paginator.count
    })

@api_view(['GET'])
def detail(request, id):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return Response({'error': 'Bài viết không tồn tại'}, status=404)
    
    # Nếu là Private, bắt buộc phải là chủ bài viết
    if post.status == 'private':
        user_id = request.GET.get('user_id')
        if not user_id or post.author_user_id != int(user_id):
            return Response({'error': 'Bài viết riêng tư'}, status=403)
    
    comments = post.comments.all().order_by('-created_at')
    return Response({
        'post': PostSerializer(post).data,
        'comments': CommentSerializer(comments, many=True).data
    })
@api_view(['GET'])
def contact(request):
    return Response({
        'message': 'Welcome to contact API',
        'email': 'contact@example.com',
        'phone': '123-456-789'
    })


# ==================== 2. CÁC HÀM SERVICE AI ====================

def ask_openrouter(prompt):
    """Gọi API OpenRouter qua pool các model miễn phí hoạt động ổn định"""
    # ⚠️ THAY THẾ CHUỖI DƯỚI ĐÂY BẰNG API KEY THẬT CỦA BẠN (Bắt đầu bằng sk-or-...)
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("Thiếu OPENROUTER_API_KEY trong .env")
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Danh sách model miễn phí hỗ trợ tiếng Việt tốt và ít nghẽn tải
    models_pool = [
        "openrouter/free"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://127.0.0.1:8000",
        "X-Title": "Laravel Django AI Blog"
    }
    
    last_error = ""
    
    for model in models_pool:
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            print(f"[OpenRouter] Đang kết nối máy chủ: {model}...")
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            res_json = response.json()
            
            print(f"[OpenRouter Response LOG]: {res_json}")
            
            if 'choices' in res_json and len(res_json['choices']) > 0:
                print(f"-> [OpenRouter] Phản hồi thành công từ: {model}")
                return res_json['choices'][0]['message']['content']
                
            elif 'error' in res_json:
                error_msg = res_json['error'].get('message', 'Provider returned error')
                print(f"-> [OpenRouter] Máy chủ {model} từ chối: {error_msg}")
                last_error = f"{model} ({error_msg})"
                continue 
                
        except Exception as e:
            print(f"-> [OpenRouter] Lỗi kết nối mạng với {model}: {str(e)}")
            last_error = str(e)
            continue
            
    return f"[OpenRouter Error]: Không có máy chủ free nào phản hồi. Chi tiết lỗi cuối: {last_error}"


def ask_gemini_direct(prompt):
    """Gọi trực tiếp API Google Gemini không qua trung gian (Dự phòng)"""
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={api_key}"
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Thiếu GEMINI_API_KEY trong .env")
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        res_json = response.json()
        
        if 'candidates' in res_json and len(res_json['candidates']) > 0:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in res_json:
            return f"[Gemini Direct Error]: {res_json['error']['message']}"
        
        return "[Gemini Direct Error]: Cấu trúc phản hồi không xác định."
    except Exception as e:
        return f"[Gemini Direct Error]: Không thể kết nối tới AI. {str(e)}"


# ==================== 3. API: TẠO BÌNH LUẬN ====================

@api_view(['POST'])
def create_comment(request, post_id):
    """Tiếp nhận bình luận từ Laravel, lưu và kích hoạt bot trả lời tự động"""
    post_object = get_object_or_404(Post, id=post_id)
    
    user_id = request.data.get('user_id')
    if user_id:
        author = get_object_or_404(User, id=user_id)
    else:
        author = User.objects.first()

    serializer = CommentSerializer(data=request.data, partial=True)
    
    if serializer.is_valid():
        user_comment_content = serializer.validated_data['content']
        
        # 1. Lưu bình luận của độc giả trước
        serializer.save(post=post_object, author=author)
        
        # 2. Đọc dữ liệu ngầm và cắt ngắn nội dung bài viết để tiết kiệm token hệ thống miễn phí
        blog_title = request.data.get('post_title') or post_object.title
        raw_content = request.data.get('post_content') or post_object.description
        blog_content = raw_content[:800] + "..." if len(raw_content) > 800 else raw_content
        
        # Thiết lập Prompt tối ưu dung lượng ký tự gửi đi
        full_context_prompt = f"""
        Bạn là một trợ lý AI thân thiện phản hồi bình luận trên blog. 
        Hãy đọc nhanh thông tin bài viết sau để trả lời độc giả:
        - Tiêu đề: {blog_title}
        - Tóm tắt nội dung: {blog_content}

        Bình luận của độc giả: "{user_comment_content}"

        Yêu cầu: Viết câu trả lời ngắn gọn (dưới 3 câu), tự nhiên, trực tiếp bằng tiếng Việt.
        """
        
        # 3. Lựa chọn luồng AI dựa vào biến ai_type
        ai_type = request.data.get('ai_type', 'openrouter')
        
        if ai_type == 'gemini':
            ai_response = ask_gemini_direct(full_context_prompt)
            bot_name = "AI_Gemini_Bot"
        else:
            ai_response = ask_openrouter(full_context_prompt)
            bot_name = "AI_OpenRouter_Bot"
            
        ai_response_str = str(ai_response).strip()
        
        ai_bot_user, _ = User.objects.get_or_create(
            username=bot_name, 
            defaults={'email': f"{bot_name}@blog.com"}
        )

        # 4. Kiểm tra chuỗi trả về xem có chứa ký tự thông báo lỗi hay không
        if "Error" not in ai_response_str and ai_response_str:
            Comment.objects.create(
                post=post_object,
                author=ai_bot_user,
                content=ai_response_str
            )
            msg = 'Đăng bình luận thành công và AI đã phản hồi!'
        else:
            Comment.objects.create(
                post=post_object,
                author=ai_bot_user,
                content=f"⚠️ [Hệ thống Bot lỗi]: {ai_response_str}"
            )
            msg = 'Bình luận đã đăng, nhưng Bot AI đang gặp sự cố kết nối.'
        
        all_comments = post_object.comments.all().order_by('-created_at')
        return Response({
            'message': msg,
            'comments': CommentSerializer(all_comments, many=True).data
        }, status=201)
        
    print("Lỗi cụ thể của Serializer:", serializer.errors)
    return Response(serializer.errors, status=400)