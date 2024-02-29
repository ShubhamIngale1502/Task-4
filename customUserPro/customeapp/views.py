from .serializer import UserSerializer
from .models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes,authentication_classes
import logging
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .utils import EmailThread
from .token import account_activation_token
from django.conf import settings
from django.contrib.sites.shortcuts import  get_current_site
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from .permission import IsOwnerIsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger('mylogger')

@api_view(http_method_names=(['POST']))
def user_create(request):
    if request.method == 'POST':
        try:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            obj.is_active = False
            obj.save()
           
            domain = get_current_site(request=request).domain
            token = account_activation_token.make_token(obj)
            uid = urlsafe_base64_encode(force_bytes(obj.pk))
            relative_url = reverse('activate',kwargs={'uid': uid, 'token':token})
            absolute_url = f'http://%s'%(domain+relative_url,)
            message = "Hello %s,\n\tThank you for creating account with us. please click on the link below"\
                "to activate your account\n %s"%(obj.username,absolute_url,)
            subject = "Account Activation Email"
            EmailThread(subject=subject, message=message, recipient_list=[obj.email], from_email=settings.EMAIL_HOST_USER).start()
            return Response({"Message":"Please check your email to activate your account"},status=201)
        except Exception as e :
            print(e)
            logger.error("Error in Creating the User")
            return Response(data=serializer.errors, status=404)
        

@api_view()
def useraccountActivate(request,uid,token):
    if request.method == 'GET':
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk= user_id)
        except(TypeError,ValueError,OverflowError,User.DoesNotExist)as e:
            return Response(data={'details':'there is an Error'},status=400)
        if account_activation_token.check_token(user=user, token=token):
            user.is_active = True
            user.save()
            return Response(data={'details':'Account Activated SuccesFully'},status=200)
        return Response(data={'details':'Account link Invalid'},status=400)
    
# @api_view(['POST'])
# def  createUser(request):
#     if request.method == 'POST':
#         try:
#             serializer = UserSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             logger.info('Student Created SuccesFylly')
#             user_email = request.user.email
#             subject = 'Registration Successful'
#             message = 'User Created Succesfully'
#             if user_email:
#                 EmailThread(
#                     subject =subject,
#                     message=message,
#                     from_email= settings.EMAIL_HOST_USER,
#                     recipient_list=[user_email]
#                 ).start()
#                 return Response(data={'details:Email Send SuccesFully'})
#             return Response(data=serializer.data, status=201)
#         except:
#             logger.error("Error in Creating the Student")
#             return Response(data=serializer.errors, status=404)
        
@api_view(http_method_names=('GET',))  
@authentication_classes([JWTAuthentication])
@permission_classes([IsOwnerIsAuthenticated])
def fetchData(request):
    if  request.method=='GET':
        try:
            obj = User.objects.all()
            serializer = UserSerializer(obj, many = True)
            logger.info('Users Fetched Successfully')
            return Response(data=serializer.data,status=201)
        except:
            logger.info('User Created with Error')
            return Response(data={'details':'It has some Error'},status=400)
        
@api_view(['GET','PUT','PATCH',"DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsOwnerIsAuthenticated])
def manageUser(request,pk):
    obj = get_object_or_404(User,pk=pk)
    if request.method == "GET":
        try:
            serializer = UserSerializer(obj)
            logger.info('Users Fetched Successfully')
            return Response(data=serializer.data,status=201)
        except:
            logger.info('User Created with Error')
            return Response(data={'details':'It has some Error'})
        
    if request.method == 'PUT':
        if request.user == obj:
            try:
                serializer = UserSerializer(data=request.data, instance=obj)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                logger.info('Data Updated Succesfully')
                return Response(data=serializer.data, status=205)
            except:
                logger.error("It Has Some Errors")
                return Response(data=serializer.errors, status=404)
        return Response(data={'detail': 'You do not have permission to perform this action'}, status=401)
    
    if request.method == 'PATCH':
        if request.user == obj:
            try:
                serializer = UserSerializer(data=request.data, instance=obj, partial = True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                logger.info('Data Updated Succesfully')
                return Response(data=serializer.data, status=205)
            except:
                logger.error("It Has Some Errors")
                return Response(data=serializer.errors, status=404)
        return Response(data={'detail': 'You do not have permission to perform this action'}, status=401)
        
    if request.method == 'DELETE':
        if request.user == obj:
            try:
                obj.delete()
                logger.info('User Deleted Successfully')
                return Response(data=None,status=206) 
            except:
                logger.error('It Has Some Error in  Deleting the Data')
                return Response(data={'details':'No Content Found'},status=206) 
        return Response(data={'detail': 'You do not have permission to perform this action'}, status=401)