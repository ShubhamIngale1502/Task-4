from rest_framework import serializers
from django.contrib.auth import get_user_model
from taskapp.serializer import TaskSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    user_task = TaskSerializer(read_only=True, many=True)
    tasks = TaskSerializer(read_only=True, many=True)
    
    class Meta:
        model = User
        fields = ('username', 'password','id','email','first_name','last_name','gender','role','pincode','address','city', 'company','user_task','tasks')
    
    def create(self, validated_data):
        obj = User.objects.create_user(**validated_data)
        obj.is_active = False
        obj.save()
        return obj
    
    def update(self, instance, validated_data):
        obj = super().update(instance, validated_data)
        if 'password' in validated_data:
            obj.set_password(validated_data['password'])
            obj.save()
        return obj