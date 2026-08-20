from rest_framework import serializers
from django.contrib.auth.models import User
from picAI.models import PictureAI
from posts.models import Post, Tag
from user_profile.models import Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ['user', 'image', 'description']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class PostSerializer(serializers.ModelSerializer):
    # Sửa từ PostSerializer thành TagSerializer để map đúng với trường ManyToMany 'tag' của model Post
    tag = TagSerializer(many=True, read_only=True) 
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'author', 'img_thumbnail', 'tag', 'created_at', 'updated_at']

class PictureAISerializer(serializers.ModelSerializer):
    class Meta:
        model = PictureAI
        # Sửa từ 'imgAI' thành 'img_AI' cho khớp chính xác với khai báo trong Model PictureAI
        fields = ['id', 'img_AI', 'description', 'created_at', 'updated_at']