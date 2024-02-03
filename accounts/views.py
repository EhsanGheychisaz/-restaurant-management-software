
from .permissions import checkPermission_for_account, isCustomer
from .serializers import *
from .models import customer, image,imageShip, complex, bannerShip
from .utils import otp, bestsellingItems, generateQR
from .authenticate import CustomAuthentication
from .createPermission import MetaMenuPermissions
from menu.models import Menu
from menu.serializers import menuSerilizers, itemSeriliazerFull

from rest_framework import status, permissions, authentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.contrib.auth.models import User
from django.db.models import Q  # New
from django.conf import settings 
from django.core.cache import cache
from django.core.files import File

from fuzzywuzzy import fuzz
from PIL import Image
from pathlib import Path
import os, sys

import traceback


class CsrfExemptSessionAuthentication(authentication.SessionAuthentication):
    def enforce_csrf(self, request):
        return


#***User (Customers and Complex) - AllowAny
class sendOtpUser(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (JSONParser,)
    authentication_classes = (
     CsrfExemptSessionAuthentication, authentication.SessionAuthentication,CustomAuthentication)

    def post(self, request):
        try:
            if request.user.is_authenticated:
                if complex.objects.filter(owner=request.user).exists():
                    return Response({"loggedIn":True,"user":str(request.user),"name":str(complex.objects.get(owner=request.user))},status= status.HTTP_400_BAD_REQUEST)
                return Response({"loggedIn":True,"user":str(request.user)},status= status.HTTP_400_BAD_REQUEST)

            data = request.data
            phoneNumber = data.get('phoneNumber', None)
            assert phoneNumber, 'phoneNumber key not found'
            isCustomer = data.get('isCustomer', None)
            assert isCustomer!=None, 'isCustomer key not found'
            if isCustomer:
                customerQ = customer.objects.filter(phoneNumber=phoneNumber).exists()
                if customerQ:
                    response , tokenCache = otp(phoneNumber, customerQ, 'customer')
                    if response and tokenCache:
                        return Response({'userExists':True, 'otpSend': True, 'isCustomers': True}, 
                              status= status.HTTP_200_OK)
                    else:
                        return Response({'userExists':True,'otpSend': False, 'isCustomers': True}, 
                              status=status.HTTP_424_FAILED_DEPENDENCY)
                else:
                    response , tokenCache = otp(phoneNumber, customerQ, 'customer')
                    if response and tokenCache:
                        return Response({'userExists':False, 'otpSend': True, 'isCustomers': True}, 
                              status= status.HTTP_200_OK)
                    else:
                        return Response({'userExists':False,'otpSend': False, 'isCustomers': True}, 
                              status=status.HTTP_424_FAILED_DEPENDENCY)
            else:
                complexQ = complex.objects.filter(phoneNumber=phoneNumber).exists()
                workerQuery = worker.objects.filter(phoneNumber=phoneNumber).exists()
                if complexQ:
                    response , tokenCache = otp(phoneNumber, complexQ, 'complex')
                    if response and tokenCache:
                        return Response({'userExists':True, 'otpSend': True, 'isComplex': True}, 
                              status= status.HTTP_200_OK)
                    else:
                        return Response({'userExists':True,'otpSend': False, 'isComplex': True}, 
                              status=status.HTTP_424_FAILED_DEPENDENCY)
                elif workerQuery:
                    response , tokenCache = otp(phoneNumber, workerQuery, 'worker')
                    if response and tokenCache:
                        return Response({'userExists':True, 'otpSend': True, 'isWorker': True}, 
                              status= status.HTTP_200_OK)
                    else:
                        return Response({'userExists':True,'otpSend': False, 'isWorker': True}, 
                              status=status.HTTP_424_FAILED_DEPENDENCY)
                else:
                    response , tokenCache = otp(phoneNumber, complexQ, 'complex')
                    if response and tokenCache:
                        return Response({'userExists':False, 'otpSend': True, 'isComplex': True}, 
                              status= status.HTTP_200_OK)
                    else:
                        return Response({'userExists':False,'otpSend': False, 'isComplex': True}, 
                              status=status.HTTP_424_FAILED_DEPENDENCY)
        except Exception as e:
            logger.exception('OPPS ...')
            return Response({'detail': str(e)}, status = status.HTTP_400_BAD_REQUEST)

class verifyUser(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (JSONParser,)

    authentication_classes = (
         CsrfExemptSessionAuthentication, authentication.SessionAuthentication,CustomAuthentication)

    def post(self, request):
        try:
            if request.user.is_authenticated:
                return Response({"loggedIn":True,"user":str(request.user)},status=status.HTTP_400_BAD_REQUEST)

            data = request.data
            phoneNumber = data.get('phoneNumber', None)
            assert phoneNumber, 'phoneNumber key not found'
            isCustomer = data.get('isCustomer', None)
            assert isCustomer!=None, 'isCustomer key not found'
            token = data.get('token', None)
            assert token, 'token key not found'
            dataCache = cache.get(str(phoneNumber))
            if not dataCache:
                    return Response({'detail': 'phone number not exists in cache'},
                     status=status.HTTP_404_NOT_FOUND)

            tokenCache = dataCache.get('token')
            verifyUser = dataCache.get('verify')
            existsUser = dataCache.get('exists')
            roleUser = dataCache.get('role')
            
            if isCustomer:
                if tokenCache == token:
                    if verifyUser and existsUser and roleUser=='customer':
                        cust = customer.objects.get(phoneNumber=phoneNumber)
                        response = Response()
                        data = request.data
                        my_data=self._custome_login(data)
                        response.set_cookie(
                        key = settings.SIMPLE_JWT['AUTH_COOKIE'], 
                        value = my_data["token"],
                        expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                        secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                        httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                        samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
                        #csrf.get_token(request)
                        response.data = {"data":my_data,'userExists':True, 'validToken':True,
                        'Userlogin': True, 'isCustomer': True, 'user': cust.id}
                        cache.delete(str(phoneNumber))
                        response.status_code=status.HTTP_200_OK
                        return response
                        # login(request, cust.user)
                        # cache.delete(str(phoneNumber))
                        # return Response ({'userExists':True, 'validToken':True, 
                        #                    'Userlogin': True, 'isCustomer': True, 'user': cust.id},
                        #                    status=status.HTTP_200_OK)
                    if not verifyUser and not existsUser and roleUser =='customer':
                        data = {'token': tokenCache, 'verify': True, 'exists': False, 'role':'customer'}
                        cache.set(str(phoneNumber), data, 500)
                        return Response ({'userExists':False, 'validToken':True, 
                                            'Userlogin': False, 'isCustomer': True},
                                            status=status.HTTP_202_ACCEPTED)

                return Response({'validToken':False, 'Userlogin': False},
                                status = status.HTTP_406_NOT_ACCEPTABLE)
            else:
                if tokenCache == token:
                    if verifyUser and existsUser and roleUser =='complex':
                        comp = complex.objects.get(phoneNumber=phoneNumber)
                        response = Response()
                        data = request.data
                        my_data=self._custome_login(data)
                        response.set_cookie(
                        key = settings.SIMPLE_JWT['AUTH_COOKIE'], 
                        value = my_data["token"],
                        expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                        secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                        httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                        samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
                        #csrf.get_token(request)
                        response.data = { "data":my_data,'userExists':True, 'validToken':True, 
                                            'Userlogin': True, 'isComplex': True, 'user': comp.id,"name":comp.name}
                        cache.delete(str(phoneNumber))
                        response.status_code=status.HTTP_200_OK
                        return response
                        # login(request, comp.owner)
                        # cache.delete(str(phoneNumber))
                        # return Response ({'userExists':True, 'validToken':True, 
                        #                    'Userlogin': True, 'isComplex': True, 'user': comp.id},
                        #                    status=status.HTTP_200_OK)
                    elif not verifyUser and not existsUser and roleUser=='complex':
                        data = {'token': tokenCache, 'verify': True, 'exists': False, 'role':'complex'}
                        cache.set(str(phoneNumber), data, 600)
                        return Response ({'userExists':False, 'validToken':True, 
                                            'Userlogin': False, 'isComplex': True},
                                            status=status.HTTP_202_ACCEPTED)

                    elif verifyUser and existsUser and roleUser =='worker':
                        workerQuery = worker.objects.get(phoneNumber=phoneNumber)
                        response = Response()
                        data = request.data
                        my_data=self._custome_login(data)
                        response.set_cookie(
                        key = settings.SIMPLE_JWT['AUTH_COOKIE'], 
                        value = my_data["token"],
                        expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                        secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                        httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                        samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
                        #csrf.get_token(request)
                        response.data = { "data":my_data,"userExists":True, "validToken":True, 
                                            "Userlogin": True, "isWorker": True, 
                                            "user": workerQuery.id,"phoneNumber":workerQuery.phoneNumber,
                                            "permission": workerQuery.permission,
                                            "name":workerQuery.complex.name}
                        cache.delete(str(phoneNumber))
                        response.status_code=status.HTTP_200_OK
                        return response
                        # login(request, comp.owner)
                        # cache.delete(str(phoneNumber))
                        # return Response ({'userExists':True, 'validToken':True, 
                        #                    'Userlogin': True, 'isComplex': True, 'user': comp.id},
                        #                    status=status.HTTP_200_OK)
                    elif not verifyUser and not existsUser and roleUser=='worker':
                        return Response ({"detail":"worker not allow to login"}, status=status.HTTP_409_CONFLICT)

                return Response({'validToken':False, 'Userlogin': False},
                        status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            print('OPPS ...')
            return Response ({'detial': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _custome_login(self,otp_obj):
        query = User.objects.filter(username=otp_obj['phoneNumber'])
        if query.exists():
            
            user = query.first()
        else:
            pass
            #   user = User.objects.create(username=otp_obj['phoneNumber'] )
            
        refresh = RefreshToken.for_user(user)
        return GetTokenSerializer({
            'refresh': str(refresh),
            'token': str(refresh.access_token),
        }).data

#***User (Customers and Complex) - IsAuthenticated
class logoutUser(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (JSONParser,)
    authentication_classes = (
    CustomAuthentication , CsrfExemptSessionAuthentication, authentication.SessionAuthentication)

    def post(self, request):
        try:
            access= request.META.get('HTTP_AUTHORIZATION', '')
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.exception('OPPS ...')
            return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)


#***Customers - AllowAny
class signUpCustomer(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (JSONParser,)
    
    authentication_classes = (
       CustomAuthentication , CsrfExemptSessionAuthentication, authentication.SessionAuthentication,)

    def post(self, request):
        try:
            if request.user.is_authenticated:
                return Response({"loggedIn":True,"user":str(request.user)},status=status.HTTP_400_BAD_REQUEST)
            data = request.data
            cust = data.get('customer', None)
            assert cust, 'customer key not found'
            phoneNumber = cust.get('phoneNumber', None)
            assert phoneNumber, 'phoneNumber key not found'
            dataCache = cache.get(str(phoneNumber))
            ruls = cust.get('acceptedRules', None)
            if not ruls:
                return Response({'detail': 'user not accepted rules'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
            if not dataCache:
                return Response ({'detail': 'phone number not exists in cache'}, 
                                status=status.HTTP_404_NOT_FOUND)
            
            verifyUser = dataCache.get('verify')
            existsUser = dataCache.get('exists')
            roleUser = dataCache.get('role')

            if verifyUser and not existsUser and roleUser =='customer':
                serializer = UserSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    customerQ = customer.objects.get(phoneNumber=phoneNumber)
                    response = Response()
                    my_data=self._custome_login(request.data)
                    response.set_cookie(
                    key = settings.SIMPLE_JWT['AUTH_COOKIE'], 
                    value = my_data["token"],
                    expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
                    #csrf.get_token(request)
                    response.data = { "data":my_data,'userCreated':True, 'Userlogin': True, 
                        'isCustomer': True, 'user': serializer.data }
                    response.status_code = status.HTTP_201_CREATED
                    cache.delete(str(phoneNumber))
                    return response
                    # login(request, customerQ.user)
                    # cache.delete(str(phoneNumber))
                    # return Response({'userCreated': True, 'userLogin': True, 'user':serializer.data}, 
                            # status = status.HTTP_201_CREATED)
                else:
                    data = {}
                    error_list = []
                    for key in serializer.errors.keys():
                        if key == 'customer':
                            for k in serializer.errors['customer']:
                                data[k] = False
                                error_list.append(serializer.errors['customer'][k])
                        else:
                            data[key] = False
                            error_list.append(serializer.errors[key])
                    
                    data['errorDetails'] = error_list
                    data['userCreated'] =False
                    return Response (data,status = status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response ({'userCreated': False, 'userLogin': False, 
                                'userVerify': False},
                                status = status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            print('OPPS ...')
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def _custome_login(self,otp_obj):
        #User = get_user_model()
        query = User.objects.filter(username=otp_obj['customer']['phoneNumber'])
        # print(query.exists())
        if query.exists():
            
            user = query.first()
        else:
            pass
            #   user = User.objects.create(username=otp_obj['phoneNumber'] )
            
        refresh = RefreshToken.for_user(user)

        return GetTokenSerializer({
            'refresh': str(refresh),
            'token': str(refresh.access_token),
            
        }).data


#***Complex - AllowAny
class signUpComplex(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (JSONParser,)

    authentication_classes = (
       CustomAuthentication , CsrfExemptSessionAuthentication, authentication.SessionAuthentication,)

    def post(self, request):
        try:
            if request.user.is_authenticated:
                return Response({"loggedIn":True,"user":str(request.user)},status=status.HTTP_400_BAD_REQUEST)
            data = request.data
            phoneNumber = data.get('username', None).split()[0]
            assert phoneNumber, 'username key not found'
            dataCache = cache.get(str(phoneNumber))
            if not dataCache:
                return Response ({'detail': 'phone number not exists in cache'}, 
                                status=status.HTTP_404_NOT_FOUND)
            
            verifyUser = dataCache.get('verify')
            existsUser = dataCache.get('exists')
            roleUser = dataCache.get('role')

            if verifyUser and not existsUser and roleUser =='complex':
                ser = ownerComplexSerializer(data=request.data)
                if ser.is_valid():
                    ser.save()
                    comp = complex.objects.get(phoneNumber=phoneNumber)
                    response = Response()
                    my_data=self._custome_login(request.data)
                    response.set_cookie(
                    key = settings.SIMPLE_JWT['AUTH_COOKIE'], 
                    value = my_data["token"],
                    expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
                    #csrf.get_token(request)
                    response.data = { "data":my_data,'userCreated':True, 'Userlogin': True, 
                        'isComplex': True, 'user': ser.data }
                    response.status_code = status.HTTP_201_CREATED
                    cache.delete(str(phoneNumber))
                    return response
                    # login(request, comp.owner)
                    # cache.delete(str(phoneNumber))
                    # return Response({'userCreated': True, 'userLogin': True, 'user':ser.data}, 
                    #                 status=status.HTTP_201_CREATED)
                else:
                    data = {}
                    error_list = []
                    for key in ser.errors.keys():
                        if key == 'complex':
                            for k in ser.errors['complex']:
                                data[k] = False
                                error_list.append(ser.errors['complex'][k])
                        else:
                            data[key] = False
                            error_list.append(ser.errors[key])
                    data['errorDetails'] = error_list
                    data['userCreated'] = False
                    return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
            else :
                return Response ({'userCreated': False, 'userLogin': False, 
                                'userVerify': False},
                                status = status.HTTP_401_UNAUTHORIZED)
        except Exception as e :
            print('OPPS ...')
            return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)
    
    def _custome_login(self,otp_obj):
        #User = get_user_model()
        query = User.objects.filter(username=otp_obj['username'])
        # print(query.exists())
        if query.exists():
            
            user = query.first()
        else:
            pass
            #   user = User.objects.create(username=otp_obj['phoneNumber'] )
            
        refresh = RefreshToken.for_user(user)

        return GetTokenSerializer({
            'refresh': str(refresh),
            'token': str(refresh.access_token),
            
        }).data

#*** Complex Owner
class getlogo(APIView):
    #TODO remove basicAuthentication
    permission_classes = (checkPermission_for_account,)
    authentication_classes = (
       CustomAuthentication , CsrfExemptSessionAuthentication, authentication.SessionAuthentication,
       authentication.BasicAuthentication)
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        try:
            up_file = request.FILES['logo']
            try:
                complexQuery = complex.objects.get(owner=request.user)
            except:
                workerQuery = worker.objects.get(user=request.user)
                complexQuery = workerQuery.complex
            complexQuery.logo = up_file
            complexQuery.logo_tumbnail = up_file
            complexQuery.save()
            complexSer = complexSerializerFull(complexQuery)
            return Response(complexSer.data, status=status.HTTP_200_OK)
        except Exception as e :
            print('OPPS ...')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)            
            return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            try:
                complexQuery = complex.objects.get(owner=request.user)
            except:
                workerQuery = worker.objects.get(user=request.user)
                complexQuery = workerQuery.complex
            complexQuery.logo.delete()
            complexQuery.logo_tumbnail.delete()
            complexQuery.save()
            return Response({'logo':"logo removed"}, status=status.HTTP_200_OK)
        except Exception as e :
            print('OPPS ...')
            return Response({'detail':str(e)}, status = status.HTTP_400_BAD_REQUEST)

class getPicComplex(APIView):
    #TODO remove basicAuthentication
    permission_classes = (checkPermission_for_account,)
    authentication_classes = (
       CustomAuthentication , CsrfExemptSessionAuthentication, authentication.SessionAuthentication,
       authentication.BasicAuthentication)
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        try:
            up_file = request.FILES['image']
            titlE = request.GET.get('title')
            try:
                complexQuery = complex.objects.get(owner=request.user)
            except:
                workerQuery = worker.objects.get(user=request.user)
                complexQuery = workerQuery.complex
            img = image.objects.create(pic=up_file,pic_tumbnail=up_file,title=titlE)
            imgship = imageShip.objects.create(image=img,foodcomplex=complexQuery)
            complexSer = complexSerializerFull(complexQuery)
            return Response(complexSer.data, status=status.HTTP_200_OK)
        except Exception as e :
            print('OPPS ...')
            return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        try:
            imge = request.GET.get("img")
            img = image.objects.get(pic=imge)
            try:
                complexQuery = complex.objects.get(owner=request.user)
            except:
                workerQuery = worker.objects.get(user=request.user)
                complexQuery = workerQuery.complex
            imgship = imageShip.objects.filter(image=img,foodcomplex=complexQuery)
            assert imgship.exists() , "is not yours"
            img.pic.delete()
            img.pic_tumbnail.delete()
            img.delete()
            return  Response({"pic": "delete successfully"}, status=status.HTTP_200_OK)
        except Exception as e :
            print('OPPS ...')
            return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)

class getBannerComplex(APIView):
    #TODO remove basicAuthentication
    permission_classes = (checkPermission_for_account,)
    authentication_classes = (
       CustomAuthentication , CsrfExemptSessionAuthentication, 
       authentication.SessionAuthentication, authentication.BasicAuthentication)
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        try:
            up_file = request.FILES['image']
            titlE = request.GET.get('title')
            try:
                complexQuery = complex.objects.get(owner=request.user)
            except:
                workerQuery = worker.objects.get(user=request.user)
                complexQuery = workerQuery.complex
            img = image.objects.create(pic=up_file,pic_tumbnail=up_file,title=titlE)
            banner = bannerShip.objects.create(banner=img,foodcomplex=complexQuery)
            complexSer = complexSerializerFull(complexQuery)
            return Response(complexSer.data, status=status.HTTP_200_OK)
        except Exception as e :
            print('OPPS ...')
            return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        try:
            imge = request.GET.get("banner")
            img = image.objects.get(pic=imge)
            try:
                complexQuery = complex.objects.get(owner=request.user)
            except:
                workerQuery = worker.objects.get(user=request.user)
                complexQuery = workerQuery.complex
            banner = bannerShip.objects.filter(banner=img,foodcomplex=complexQuery)
            assert banner.exists() , "is not yours"
            img.pic.delete()
            img.pic_tumbnail.delete()
            img.delete()
            return  Response({"banner": "delete successfully"}, status=status.HTTP_200_OK)
        except Exception as e :
            print('OPPS ...')
            return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)

class updateComplex(APIView):
    #TODO remove basicAuthentication
    permission_classes = (checkPermission_for_account,)
    parser_classes = (JSONParser,)

    authentication_classes = (
       CustomAuthentication , CsrfExemptSessionAuthentication, authentication.SessionAuthentication,
        authentication.BasicAuthentication)

    def post(self, request):
        try:
            data = request.data
            complexId = data.pop('complexId', None)
            assert complexId, 'complexId key not found'
            try:
                complexQuery = complex.objects.get(owner=request.user)
            except:
                workerQuery = worker.objects.get(user=request.user)
                complexQuery = workerQuery.complex        
            assert complexQuery == complex.objects.get(id=complexId), 'complexQuery not exists'
            serializer = updateComplexSerializer(complexQuery, data=request.data, partial=True)
            if serializer.is_valid():
                complexUpdated = serializer.save()
                complexSer = complexSerializerFull(complexUpdated)
                return Response(complexSer.data, status=status.HTTP_202_ACCEPTED)
            else:
                data = {}
                error_list = []
                for key in serializer.errors.keys():
                    data[key] = False
                    error_list.append(serializer.errors[key])
                data['errorDetails'] = error_list
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            print('OPPS ...')
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class generate_QRcode_complex(APIView):
    #TODO Remove BasicAuthentication
    permission_classes = (checkPermission_for_account,)
    parser_classes = (JSONParser,)

    authentication_classes = (
       CustomAuthentication , CsrfExemptSessionAuthentication, 
       authentication.SessionAuthentication, authentication.BasicAuthentication)
    parser_classes = (MultiPartParser,)

    def get(self, request):
        try:
            try:
                complexQuery = complex.objects.get(owner=request.user)
            except:
                workerQuery = worker.objects.get(user=request.user)
                complexQuery = workerQuery.complex
            if complexQuery.logo == None:
                return Response({'detail':"logo not found"}, status=status.HTTP_404_NOT_FOUND)
            
            result, path = generateQR(complexQuery.logo, complexQuery.name)
            
            path = Path(path)
            with open (path, 'rb') as f:
                complexQuery.qrCode = File(f, name=path.name)
                complexQuery.save()
            os.remove(path)
            data = dict(path=complexQuery.qrCode.path)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            print('OPPS ...')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class addEmployee(APIView):
    #TODO remove basicAuthentication
    permission_classes = (checkPermission_for_account,)
    parser_classes = (JSONParser,)

    authentication_classes = (
       CustomAuthentication , CsrfExemptSessionAuthentication, authentication.SessionAuthentication, authentication.BasicAuthentication)

    def post(self, request):
        # dataFormat= {
        #     "first_name":"",
        #     "last_last":"",
        #     "worker":{
        #         "phoneNumber":"",
        #         "roleName":""
        #     }
        #     "permissions":["menu"]
        # }
        try:
            data = request.data
            permission = data.pop("permissions")
            assert permission, 'permissons key not found'
            try:
                complexQuery = complex.objects.get(owner=request.user)
            except:
                workerQuery = worker.objects.get(user=request.user)
                complexQuery = workerQuery.complex
            
            workerQuery = worker.objects.filter(phoneNumber=data.get('worker').get('phoneNumber'))
            if workerQuery.exists():
                return Response({'detail':"user registered before as worker"},
                    status=status.HTTP_409_CONFLICT)
                
            data['worker']['complex'] = complexQuery.id
            data['worker']['permission'] = permission
            workerSer = workerSerializer(data=data)
            if workerSer.is_valid():
                workerSaved = workerSer.save()
            else:
                return Response(workerSer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            res = {}
            res['data'] = workerSer.data
            res['permissions'] = list()
            res['permissionsWithError'] = list()
            
            workerQuery = worker.objects.get(phoneNumber=workerSaved.username)
            metaMenuPer = MetaMenuPermissions(workerQuery.user)
            
            for perm in permission:
                if perm == "menu":
                    status_perm_menu = metaMenuPer.menu_permissions_add() 
                    if status_perm_menu:
                        res['permissions'].append('menu')
                    else:
                        res['permissionsWithError'].append('menu')
                elif perm == "order":
                    status_perm_order = metaMenuPer.order_permissions_add()
                    if status_perm_order:
                        res['permissions'].append('order')
                    else:
                        res['permissionsWithError'].append('order')
                elif perm == "account":
                    status_perm_account = metaMenuPer.account_permissions_add() 
                    if status_perm_account:
                        res['permissions'].append('account')
                    else:
                        res['permissionsWithError'].append('account')                
                elif perm == "payment":
                    status_perm_payment = metaMenuPer.payment_permissions_add()
                    if status_perm_payment:
                        res['permissions'].append('payment')
                    else:
                        res['permissionsWithError'].append('payment')
                else:
                    return Response({'detail':"permission not valid"}, status=status.HTTP_406_NOT_ACCEPTABLE)

            return Response(res, status=status.HTTP_201_CREATED)

        except Exception as e:
            print('OPPS ...')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            try:
                complexQuery = complex.objects.get(owner=request.user)
            except:
                workerQuery = worker.objects.get(user=request.user)
                complexQuery = workerQuery.complex
            workerQuery = worker.objects.filter(complex=complexQuery)
            workerSer = employeeFullSerializer(workerQuery, many=True)
            return Response(workerSer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception('OPPS ...')
            return Response({"detail":str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # dataFormat= {
        # "id":3,  
        # "user":{
        #       "first_name":"", 
        #       "last_name":"", ""},
        # "roleName":""
        # "permissions":["menu"]
        # }     
        try:
            data = request.data
            permission = data.pop("permission", None)
            try:
                complexQuery = complex.objects.get(owner=request.user)
            except:
                workerQuery = worker.objects.get(user=request.user)
                complexQuery = workerQuery.complex
            workerQuery = worker.objects.get(id=data.get('id'))
            if permission:
                workerQuery.permission =None
                workerQuery.save()
                workerPerm = workerQuery.user.user_permissions.all()
                for perm in workerPerm:
                    workerQuery.user.user_permissions.remove(perm)
                data['permission']= permission
            workerSer = updateEmployeeSerializer(workerQuery, data, partial=True)
            if workerSer.is_valid():
                workerSaved = workerSer.save()
            else:
                return Response(workerSer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
            data = dict()
            data['worker'] = workerSer.data
            data['permission'] = list()
            data['permissionsWithError'] = list()
            if permission:
                metaMenuPer = MetaMenuPermissions(workerQuery.user)
                for perm in permission:
                    if perm == "menu":
                        status_perm_menu = metaMenuPer.menu_permissions_add() 
                        if status_perm_menu:
                            data['permission'].append('menu')
                        else:
                            data['permissionsWithError'].append('menu')
                    elif perm == "order":
                        status_perm_order = metaMenuPer.order_permissions_add()
                        if status_perm_order:
                            data['permission'].append('order')
                        else:
                            data['permissionsWithError'].append('order')
                    elif perm == "account":
                        status_perm_account = metaMenuPer.account_permissions_add() 
                        if status_perm_account:
                            data['permission'].append('account')
                        else:
                            data['permissionsWithError'].append('account')                
                    elif perm == "payment":
                        status_perm_payment = metaMenuPer.payment_permissions_add()
                        if status_perm_payment:
                            data['permission'].append('payment')
                        else:
                            data['permissionsWithError'].append('payment')
                    else:
                        return Response({'detail':"permission not valid"}, status=status.HTTP_406_NOT_ACCEPTABLE)

                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            print('OPPS ...')
            return Response({"detail":str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # dataFormat = {
        #     "id",
        # }
        try:
            data = request.data
            try:
                complexQuery = complex.objects.get(owner=request.user)
            except:
                workerQuery = worker.objects.get(user=request.user)
                complexQuery = workerQuery.complex
            workerQuery = worker.objects.get(id = data.get('id'))
            workerSer = employeeFullSerializer(workerQuery)
            workerQuery.delete()
            return Response(workerSer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print('OPPS ...')
            return Response({"detail":str(e)}, status=status.HTTP_400_BAD_REQUEST)

#*** AllowAny
class searchComplex(APIView):
    permission_classes = (permissions.AllowAny,)
    
    authentication_classes = (
       CustomAuthentication , CsrfExemptSessionAuthentication, authentication.SessionAuthentication,)
    
    def get(self,request):
        try:
            bestSelItems = {}
            favoriteItems = {}
            oferItems= {}
            promoteItems= {}
            complexName = request.GET.get("complex",None)
            complexId = request.GET.get("id", None)
            assert complexName or complexId,"complex name/id is required"
            try:
                comp = complex.objects.get(id=complexId)
            except:
                comp = complex.objects.get(name=complexName)

            ser = complexSerializerFull(comp)
            menu = Menu.objects.filter(complex=comp)
            menuser = menuSerilizers(menu,many=True)
            data = ser.data
            data["menu"]=menuser.data
            #***bestSelling and favorite items
            for eachMenu in menu:
                bestItem = bestsellingItems(comp, eachMenu, 4)
                if len(bestItem)>=1 and type(bestItem)==type(list()) :
                    itemQuery = eachMenu.items.filter(id__in=bestItem)
                    bestsellingSer = itemSeriliazerFull(itemQuery, many=True)
                    bestSelItems[eachMenu.name]=bestsellingSer.data

                favoriteItemsQ = eachMenu.items.filter(favoriteItem=True)
                favoriteItemSer = itemSeriliazerFull(favoriteItemsQ, many=True)
                favoriteItems[eachMenu.name] = favoriteItemSer.data

                #***promote and ofer items
                oferItems[eachMenu.name] = []
                promoteItems[eachMenu.name] = []
                itemsQ = eachMenu.items.all()
                for item in itemsQ:
                    item_all_price = item.price.all()
                    for eachPrice in item_all_price:
                        if eachPrice.discount:
                            if eachPrice.discount.active == True:
                                oferItemSer = itemSeriliazerFull(item)
                                oferItems[eachMenu.name].append(oferItemSer.data) 
                                break

                    if item.badge.get('promote',False)==True:
                        promoteItemsSer = itemSeriliazerFull(item)
                        promoteItems[eachMenu.name].append(promoteItemsSer.data) 
                #***promote and ofer items
            
            data['bestselling'] = bestSelItems
            data['favoriteItems'] = favoriteItems
            data['promoteItems'] = promoteItems
            data['offers'] = oferItems
            return Response(data, status=status.HTTP_200_OK)
            #***bestSelling and favorite items
            #return Response(data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print('OPPS ...')
            return Response ({'detial': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self,request):
        try:
            complexName = request.data.get("complex",None)
            assert complexName,"complex name is required"
            

             
            #search_query = SearchQuery(complexName)
            #comp = complex.objects.annotate(search=SearchVector("name",),).filter(search=search_query)
            
            comp = complex.objects.filter(Q(name__icontains=complexName))
            if comp.exists():
                 ser = complexSerializerFull(comp,many=True)
                 return Response(ser.data, status=status.HTTP_200_OK)
                 
            comp = complex.objects.all()
            lis = []

            for i in comp:
                r = fuzz.ratio(i.name,complexName)
                t = fuzz.ratio(complexName,i.name)
                c = (r+t)/2
                lis.append([c,i.name])
            
            lis.sort(reverse=True)
            l = [i[1] for i in lis]
            a = lambda lis:lis[1]
            if len(lis)>3:
                comp2 =  complex.objects.filter(Q(name__in=l[0:3]))
            elif len(lis)>0:
                comp2 = complex.objects.filter(Q(name__icontains=lis[0][1]))
            else:
                 return Response ({'detial': "Not Found any complex"}, status=status.HTTP_404_NOT_FOUND)

            ser = complexSerializerFull(comp2,many=True)
            #menu = Menu.objects.filter(complex=comp)
            #menuser = menuSerilizers(menu,many=True)
            #data = ser.data
            #data["menu"]=menuser.data

            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            print('OPPS ...')
            return Response ({'detial': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#*** Customer, IsAuthenticated
class customerInfo(APIView):
    #TODO remove basicAuthentication
    permission_classes = (isCustomer,)
    parser_classes = (JSONParser,)
    authentication_classes = (CustomAuthentication , CsrfExemptSessionAuthentication, authentication.SessionAuthentication, authentication.BasicAuthentication)

    def get(self, request):
        try:
            user = request.user
            customerQuery = customer.objects.get(user=user)
            customerSer = customerInfoSerializer(customerQuery)
            return Response(customerSer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print('OPPS ...')
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # dataFormat = {
        #     "user":{"first_name", "last_name"},
        #     "birthDate":"",

        # }
        try:
            data = request.data
            user = request.user

            customerQuery = customer.objects.get(user=user)
            customerSer = customerInfoSerializer(customerQuery, data, partial=True)
            if customerSer.is_valid():
                customerSer.save()
                return Response(customerSer.data, status=status.HTTP_200_OK)
            else:
                return Response(customerSer.errors, status=status.HTTP_200_OK)
                
        except Exception as e:
            print('OPPS ...')
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class checkUser(APIView):
    #TODO remove basicAuthentication
    permission_classes = (permissions.AllowAny,)
    parser_classes = (JSONParser,)
    authentication_classes = (CustomAuthentication , CsrfExemptSessionAuthentication, authentication.SessionAuthentication, authentication.BasicAuthentication)

    def get(self, request):
        try:
            who = request.GET.get('who', None)
            assert who, "Invalid request"
            if request.user.is_authenticated:
                if who == "complex":
                    complexQuery = complex.objects.get(owner=request.user)
                    complexSer = complexSerializerFull(complexQuery)
                    return Response(
                        complexSer.data, 
                        status=status.HTTP_200_OK
                    )
                elif who == 'customer':
                    customerQuery = customer.objects.get(user=request.user)
                    customerSer = customerInfoSerializer(customerQuery)
                    return Response(
                            customerSer.data, 
                            status=status.HTTP_200_OK
                    )
                elif who == 'worker':
                    workerQuery = worker.objects.get(user=request.user)
                    workerSer = employeeFullSerializer(workerQuery)
                    complexQuery = complex.objects.get(id=workerSer.data['complex'])
                    return Response(
                        dict(complex_name=workerQuery.complex.name, **workerSer.data),
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                    {"detail":"Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            else:
                return Response(
                    {"detail":"Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            print('OPPS ...')
            return Response({"detail":str(e)}, status=status.HTTP_400_BAD_REQUEST)

class complexInformation(APIView):
    permission_classes = (permissions.AllowAny,)
    
    authentication_classes = (
       CustomAuthentication , CsrfExemptSessionAuthentication, authentication.SessionAuthentication,)
    
    def get(self,request):
        try:
            data = dict()
            complexName = request.GET.get("complex",None)
            complexId = request.GET.get("id", None)
            assert complexName or complexId,"complex name/id is required"
            whatNeed = request.GET.get('need', None)
            assert whatNeed, 'need key not found'
            whatNeed = whatNeed.split(",")
            
            try:
                comp = complex.objects.get(id=complexId)
            except:
                comp = complex.objects.get(name=complexName)
            
            menu = Menu.objects.filter(complex=comp)
            
            for need in whatNeed:
                need = need.replace(" ", "")
                if need == "menu":
                    menuser = menuSerilizers(menu,many=True)
                    data["menu"]=menuser.data
                
                elif need == "best":
                    bestSelItems = dict()
                    for eachMenu in menu:
                        bestItem = bestsellingItems(comp, eachMenu, 4)
                        if len(bestItem)>=1 and type(bestItem)==type(list()) :
                            itemQuery = eachMenu.items.filter(id__in=bestItem)
                            bestsellingSer = itemSeriliazerFull(itemQuery, many=True)
                            bestSelItems[eachMenu.name]=bestsellingSer.data
                    data['bestselling'] = bestSelItems
                
                elif need == "favorite":
                    favoriteItems = dict()
                    for eachMenu in menu:
                        favoriteItemsQ = eachMenu.items.filter(favoriteItem=True)
                        favoriteItemSer = itemSeriliazerFull(favoriteItemsQ, many=True)
                        favoriteItems[eachMenu.name] = favoriteItemSer.data
                    data['favoriteItems'] = favoriteItems
                
                elif need == "offers":
                    oferItems= dict()
                    for eachMenu in menu:
                        oferItems[eachMenu.name] = []
                        itemsQ = eachMenu.items.all()
                        for item in itemsQ:
                            item_all_price = item.price.all()
                            for eachPrice in item_all_price:
                                if eachPrice.discount:
                                    if eachPrice.discount.active == True:
                                        oferItemSer = itemSeriliazerFull(item)
                                        oferItems[eachMenu.name].append(oferItemSer.data) 
                                        break
                    data['offers'] = oferItems
                
                elif need == "promote":
                    promoteItems= dict()
                    for eachMenu in menu:
                        promoteItems[eachMenu.name] = []
                        itemsQ = eachMenu.items.all()
                        for item in itemsQ:
                            if item.badge.get('promote',False)==True:
                                promoteItemsSer = itemSeriliazerFull(item)
                                promoteItems[eachMenu.name].append(promoteItemsSer.data) 
                    data['promoteItems'] = promoteItems

                else:
                    data = complexSerializerFull(comp).data

            return Response(data, status=status.HTTP_200_OK)

        
        except Exception as e:
            print('OPPS ...')
            return Response ({'detial': str(e)}, status=status.HTTP_400_BAD_REQUEST)