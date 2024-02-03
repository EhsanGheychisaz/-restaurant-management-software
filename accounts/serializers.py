from rest_framework import serializers,status
from rest_framework.exceptions import APIException

from django.utils.encoding import force_str
from django_jalali.serializers.serializerfield import JDateField

from string import ascii_uppercase, digits
from random import choices
from hashlib import sha256
import os, sys

from .models import *

class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail, field, status_code):
        if status_code is not None: self.status_code = status_code
        if detail is not None:
            self.detail = {field: force_str(detail)}
        else:
            self.detail = {'detail': force_str(self.default_detail)}

class GetTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=128, allow_null=False)
    refresh = serializers.CharField(max_length=128, allow_null=False)
    
class userFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name","last_name"]

#***Customer :
class customerSerializer(serializers.ModelSerializer):
    birthDate = JDateField()
    class Meta:
        model = customer
        # fields = ["birthDate","address","phoneNumber","acceptRuls"]
        fields = ["birthDate","phoneNumber","acceptedRules"]


    def validate(self, attrs):
        mobile = attrs.get('phoneNumber', None)
        if customer.objects.filter(phoneNumber=mobile).exists():
            raise serializers.ValidationError({'phoneNumber':('phoneNumber is already in use')})
        return super().validate(attrs)

class UserSerializer(serializers.ModelSerializer):
    customer = customerSerializer(required=True)
    class Meta:
        model = User
        fields = ['first_name', 'last_name',"customer"]

    def create(self, validated_data):
        try :
            customer_data = validated_data.pop("customer")
            validated_data['username'] = customer_data.get('phoneNumber')
            if User.objects.filter(username=validated_data['username']).exists():
                user = User.objects.get(username=validated_data.get('username'))
            else:
                user = User.objects.create_user(**validated_data)
                ran = ''.join(choices(ascii_uppercase + digits, k=64))
                password = str(sha256(ran.encode()))
                user.set_password(password)
            custom = customer.objects.create(user=user, **customer_data)
        
            # print(userProfile_data)
            return user
        except Exception as e:
            return str(e)

class customerFulllSerializer(serializers.ModelSerializer):
    user = userFullSerializer(read_only=True)
    class Meta:
            model = customer
            fields =["phoneNumber","user"]

class customerInfoSerializer(serializers.ModelSerializer):
    user = userFullSerializer()
    birthDate = JDateField()

    class Meta:
        model = customer
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.birthDate = validated_data.get('birthDate', instance.birthDate)
        instance.user.first_name = validated_data.get('user',instance.user.first_name).get('first_name', instance.user.first_name)
        instance.user.last_name = validated_data.get('user', instance.user.last_name).get('last_name', instance.user.last_name)
        instance.save()
        return instance

#***ownerComplex and Complex
class complexSerializer(serializers.ModelSerializer):
        class Meta:
            model = complex
            fields =  ["name","merchant_code","state","city","neighborhood","address","telephone","phoneNumber","Slogan",
                       "socialMedia", "emergencyCall", "location", "color", "workTime", "bio", "taxType", "dark_mode", "customer_ordering"]

class complexSerializerFull(serializers.ModelSerializer):
    complexImage = serializers.SlugRelatedField(many=True, read_only=True, slug_field="pic_url")
    banner = serializers.SlugRelatedField(many=True, read_only=True, slug_field="pic_url")
    class Meta:
        model = complex
        fields = "__all__"


class ownerComplexSerializer(serializers.ModelSerializer):
    complex = complexSerializer(required=True)
    username = serializers.CharField(validators=[])
    class Meta:
        model = User
        fields = ['first_name', 'last_name','username',"complex"]

    def create(self, validated_data):
        try :
            complex_data = validated_data.pop("complex")
            if User.objects.filter(username=validated_data.get('username')).exists():
                user = User.objects.get(username=validated_data.get('username'))
            else:
                user = User.objects.create_user(**validated_data)
                ran = ''.join(choices(ascii_uppercase + digits, k=64))
                password = str(sha256(ran.encode()))
                user.set_password(password)
            comp = complex.objects.create(owner=user, **complex_data)
            if customer.objects.filter(phoneNumber =validated_data.get("username",None)).exists():
                pass
            else:
                cust = customer.objects.create(user=user,phoneNumber=validated_data.get("username",None), 
                                        birthDate="1401-01-01",acceptedRules=True )
            # print(userProfile_data)
            return user
        except Exception as e:
            return str(e)

class updateComplexSerializer(serializers.ModelSerializer):
    class Meta:
        model = complex
        fields =  ["name","state","city","neighborhood","address","telephone",
                   "Slogan", "socialMedia", "location", "color", "workTime", "bio", "emergencyCall", "dark_mode", "customer_ordering"]

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.state = validated_data.get('state',instance.state )
        instance.city = validated_data.get('city', instance.city)
        instance.neighborhood = validated_data.get('neighborhood', instance.neighborhood)
        instance.address = validated_data.get('address', instance.address )
        instance.telephone = validated_data.get('telephone', instance.telephone )
        instance.Slogan = validated_data.get('Slogan', instance.Slogan)
        instance.socialMedia = validated_data.get('socialMedia', instance.socialMedia )
        instance.location = validated_data.get('location', instance.location)
        instance.color = validated_data.get('color', instance.color )
        instance.workTime = validated_data.get('workTime', instance.workTime )
        instance.bio = validated_data.get('bio', instance.bio )
        instance.dark_mode = validated_data.get('dark_mode', instance.dark_mode )
        instance.customer_ordering = validated_data.get('customer_ordering', instance.customer_ordering )


        return super().update(instance, validated_data)

class employeeSerializer(serializers.ModelSerializer):
    class Meta:
        model =worker
        fields = ['phoneNumber', 'roleName', 'complex', 'permission']

    def validate(self, attrs):
        mobile = attrs.get('phoneNumber', None)
        if worker.objects.filter(phoneNumber=mobile).exists():
            raise serializers.ValidationError({'phoneNumber':('phoneNumber is already in use')})
        return super().validate(attrs)

class employeeFullSerializer(serializers.ModelSerializer):
    user = userFullSerializer(read_only=True)
    class Meta:
        model =worker
        fields = "__all__"

class workerSerializer(serializers.ModelSerializer):
    worker = employeeSerializer(required=True)
    class Meta:
        model = User
        fields = ['first_name', 'last_name',"worker"]

    def create(self, validated_data):
        try :
            worker_data = validated_data.pop("worker")
            validated_data['username'] = worker_data.get('phoneNumber')
            if User.objects.filter(username= validated_data['username']).exists():
                user = User.objects.get(username=validated_data.get('username'))
            else:
                user = User.objects.create(first_name=validated_data['first_name'], last_name=validated_data['last_name'], username=validated_data['username'])
                ran = ''.join(choices(ascii_uppercase + digits, k=64))
                password = str(sha256(ran.encode()))
                user.set_password(password)
            empl = worker.objects.create(user=user, **worker_data)
            # print(userProfile_data)
            return user
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return str(e)

class updateEmployeeSerializer(serializers.ModelSerializer):
    user = userFullSerializer()
    class Meta:
        model = worker
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.roleName = validated_data.get('roleName', instance.roleName)
        instance.permission = validated_data.get('permission', instance.permission)
        instance.user.first_name = validated_data.get('user',instance.user.first_name).get('first_name', instance.user.first_name)
        instance.user.last_name = validated_data.get('user', instance.user.last_name).get('last_name', instance.user.last_name)
        instance.save()
        return instance