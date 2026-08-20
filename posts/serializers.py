from rest_framework import serializers
from django.contrib.auth.models import User
from picAI.models import PictureAI
from posts.models import Post, Tag, Comment
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

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    author_user = UserSerializer(read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'description', 'author', 'author_user',
            'status',          # <-- THÊM DÒNG NÀY
            'img_thumbnail', 'tag', 'comments',
            'created_at', 'updated_at'
        ]

class PictureAISerializer(serializers.ModelSerializer):
    class Meta:
        model = PictureAI
        fields = ['id', 'img_AI', 'description', 'created_at', 'updated_at']