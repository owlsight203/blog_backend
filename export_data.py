import os
import django
from django.core.serializers import serialize
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog.settings')
django.setup()

# Danh sách các app bạn muốn xuất dữ liệu
app_list = ['posts', 'picAI', 'user_profile']

for app_name in app_list:
    try:
        # Lấy tất cả các model thuộc app này
        app_models = apps.get_app_config(app_name).get_models()
        
        # Gom toàn bộ dữ liệu của tất cả các model trong app lại
        all_objects = []
        for model in app_models:
            all_objects.extend(model.objects.all())
            
        # Serialize dữ liệu ra chuỗi JSON với chuẩn utf-8
        data = serialize('json', all_objects, use_natural_foreign_keys=True, use_natural_primary_keys=True)
        
        filename = f'{app_name}_data.json'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(data)
            
        print(f"Export app '{app_name}' thành công vào file: {filename}!")
    except Exception as e:
        print(f"Lỗi khi export app {app_name}: {e}")

# (Tùy chọn) Xuất thêm bảng User hệ thống nếu cần lưu tài khoản đăng nhập
try:
    from django.contrib.auth.models import User
    user_data = serialize('json', User.objects.all(), use_natural_foreign_keys=True, use_natural_primary_keys=True)
    with open('users_data.json', 'w', encoding='utf-8') as f:
        f.write(user_data)
    print("Export bảng User thành công vào file: users_data.json!")
except Exception as e:
    print(f"Lỗi khi export User: {e}")