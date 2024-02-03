
from django.urls import path
from .views import *

urlpatterns = [
    path('customers/signup/',signUpCustomer.as_view(), name='signup-customers'),
    path('customers/info/',customerInfo.as_view(), name='info-customers'),
    path('check/', checkUser.as_view(), name='check-user'),
    path('otp/', sendOtpUser.as_view(), name='otp'),
    path('verify/', verifyUser.as_view(), name='verify'),
    path('logout/', logoutUser.as_view(), name='logout'),
    path('complex/signup/',signUpComplex.as_view(),name='sign up complex'),
    path('complex/update/',updateComplex.as_view(),name='update complex'),
    path("complex/search/",searchComplex.as_view(),name="search complex"),
    path("complex/getlogo/",getlogo.as_view(),name="get complex logos"),
    path("complex/getqr/",generate_QRcode_complex.as_view(),name="generate Qr code"),
    path("complex/getpic/",getPicComplex.as_view(),name="get-complex-pics"),
    path("complex/getbanner/",getBannerComplex.as_view(),name="get-complex-banners"),
    path("complex/worker/", addEmployee.as_view(), name="manage-workers"),
    path("complex/info/", complexInformation.as_view(), name="complex_info"),

]
