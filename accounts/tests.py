import json

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache

from rest_framework.test import APIClient
from rest_framework import status

from .models import customer


class customerTescase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='aliz', first_name='Alireza', last_name='Fadaei')
        self.user2 = User.objects.create(username='farnam', first_name='Farnam', last_name='Farzadkia')

        self.customer1 = customer.objects.create(user=self.user1, birthDate='1377-10-16',
                                address='isfahan', phoneNumber='09131170825', acceptRuls=False)
        self.customer1 = customer.objects.create(user=self.user2, birthDate='1379-03-02',
                                address='isfahan', phoneNumber='09131170826', acceptRuls=False)
        
        self.dataValid = {
            "first_name":"Reza",
            "last_name":"Zarean",
            "customer":{
                "birthDate":"1380-10-10",
                "address":"isfahan",
                "phoneNumber":"09131170827",
                "acceptRuls":True}
        }
#***Login Valid Tests:
    def testValid_login(self):
        client = APIClient()
        data = {
            "phoneNumber":"09131170825",
            "isCustomer":True
        }
        responses = client.post(
            reverse('otp'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'userExists':True, 'otpSend': True, 'isCustomers': True})
        self.assertEqual(responses.status_code, status.HTTP_200_OK)

        data = {
            "phoneNumber":"09131170825",
            "isCustomer":True,
            "token":"1111"
        }
        responses = client.post(
            reverse('verify'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'userExists':True, 'validToken':True, 
                                            'Userlogin': True, 'isCustomer': True})
        self.assertEqual(responses.status_code, status.HTTP_200_OK)
        
        #***Logout user
        responses = client.get(reverse('logout'))
        self.assertEqual(responses.status_code, status.HTTP_200_OK)

#***Verify Number, signup and login Valid Test
    def testValid_login_notAuth(self):
        client = APIClient()
        #*** Send Otp
        data = {
            "phoneNumber":"09131170823",
            "isCustomer":True
        }
        responses = client.post(
            reverse('otp'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'userExists':False, 'otpSend': True, 'isCustomers': True})
        self.assertEqual(responses.status_code, status.HTTP_200_OK)

        #***Verify Token
        data = {
            "phoneNumber":"09131170823",
            "isCustomer":True,
            "token":"1111"
        }
        responses = client.post(
            reverse('verify'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'userExists':False, 'validToken':True, 
                                            'Userlogin': False, 'isCustomer': True})
        self.assertEqual(responses.status_code, status.HTTP_202_ACCEPTED)
        
        #***Signup user
        data ={
            "first_name":"Reza",
            "last_name":"Zarean",
            "customer":{
                "birthDate":"1380-10-10",
                "address":"isfahan",
                "phoneNumber":"09131170823",
                "acceptRuls":"True"}
        }
        responses = client.post(
            reverse('signup-customers'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'userCreated': True, 'userLogin': True})
        self.assertEqual(responses.status_code, status.HTTP_201_CREATED)

        #***Logout user
        responses = client.get(reverse('logout'))
        self.assertEqual(responses.status_code, status.HTTP_200_OK)

#***Login InValid Tests
    def testInValid_login_tokenNotValid(self):
        client = APIClient()
        data = {
            "phoneNumber":"09131170825",
            "isCustomer":True
        }
        responses = client.post(
            reverse('otp'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'userExists':True, 'otpSend': True, 'isCustomers': True})
        self.assertEqual(responses.status_code, status.HTTP_200_OK)

        data = {
            "phoneNumber":"09131170825",
            "isCustomer":True,
            "token":"2222"
        }
        responses = client.post(
            reverse('verify'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'validToken':False, 'Userlogin': False})
        self.assertEqual(responses.status_code, status.HTTP_406_NOT_ACCEPTABLE)

#***Verify Number, signup and login InValid Test
    def testInValid_login_notAuth_tokenNotValid(self):
        client = APIClient()
        data = {
            "phoneNumber":"09131170823",
            "isCustomer":True
        }
        responses = client.post(
            reverse('otp'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'userExists':False, 'otpSend': True, 'isCustomers': True})
        self.assertEqual(responses.status_code, status.HTTP_200_OK)

        data = {
            "phoneNumber":"09131170823",
            "isCustomer":True,
            "token":"2222"
        }
        responses = client.post(
            reverse('verify'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'validToken':False, 'Userlogin': False})
        self.assertEqual(responses.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def testInValid_login_notAuth_WrongNumber(self):
        client = APIClient()
        #*** Send Otp
        data = {
            "phoneNumber":"09131170823",
            "isCustomer":True
        }
        responses = client.post(
            reverse('otp'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'userExists':False, 'otpSend': True, 'isCustomers': True})
        self.assertEqual(responses.status_code, status.HTTP_200_OK)

        #***Verify Token
        data = {
            "phoneNumber":"09131170823",
            "isCustomer":True,
            "token":"1111"
        }
        responses = client.post(
            reverse('verify'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'userExists':False, 'validToken':True, 
                                            'Userlogin': False, 'isCustomer': True})
        self.assertEqual(responses.status_code, status.HTTP_202_ACCEPTED)
        
        #***Signup user
        data ={
            "first_name":"Reza",
            "last_name":"Zarean",
            "customer":{
                "birthDate":"1380-10-10",
                "address":"isfahan",
                "phoneNumber":"09131170829",
                "acceptRuls":"True"}
        }
        responses = client.post(
            reverse('signup-customers'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'error': 'phone number not exists in cache'})
        self.assertEqual(responses.status_code, status.HTTP_404_NOT_FOUND)

    def testInValid_login_notAuth_NotVerify(self):
        client = APIClient()
        #*** Send Otp
        data = {
            "phoneNumber":"09131170823",
            "isCustomer":True
        }
        responses = client.post(
            reverse('otp'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'userExists':False, 'otpSend': True, 'isCustomers': True})
        self.assertEqual(responses.status_code, status.HTTP_200_OK)

        # #***Verify Token
        # data = {
        #     "phoneNumber":"09131170823",
        #     "isCustomer":True,
        #     "token":"1111"
        # }
        # responses = client.post(
        #     reverse('verify'), data = json.dumps(data), content_type='application/json'
        # )
        # responses_data = json.loads(responses.content)
        # self.assertEqual(responses_data, {'userExists':False, 'validToken':True, 
        #                                     'Userlogin': False, 'isCustomer': True})
        # self.assertEqual(responses.status_code, status.HTTP_202_ACCEPTED)
        
        #***Signup user
        data ={
            "first_name":"Reza",
            "last_name":"Zarean",
            "customer":{
                "birthDate":"1380-10-10",
                "address":"isfahan",
                "phoneNumber":"09131170823",
                "acceptRuls":"True"}
        }
        responses = client.post(
            reverse('signup-customers'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'userCreated': False, 'userLogin': False, 
                                'userVerify': False})
        self.assertEqual(responses.status_code, status.HTTP_401_UNAUTHORIZED)

    def testInValid_login_notAuth_notValidData(self):
        client = APIClient()
        #*** Send Otp
        data = {
            "phoneNumber":"09131170823",
            "isCustomer":True
        }
        responses = client.post(
            reverse('otp'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'userExists':False, 'otpSend': True, 'isCustomers': True})
        self.assertEqual(responses.status_code, status.HTTP_200_OK)

        #***Verify Token
        data = {
            "phoneNumber":"09131170823",
            "isCustomer":True,
            "token":"1111"
        }
        responses = client.post(
            reverse('verify'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses_data, {'userExists':False, 'validToken':True, 
                                            'Userlogin': False, 'isCustomer': True})
        self.assertEqual(responses.status_code, status.HTTP_202_ACCEPTED)
        
        #***Signup user
        data ={
            "first_name":"Reza",
            "last_name":"Zarean",
            "customer":{
                "birthDate":"1380-10-10hhhhhh",
                "address":"isfahan",
                "phoneNumber":"09131170823",
                "acceptRuls":"True"}
        }
        responses = client.post(
            reverse('signup-customers'), data = json.dumps(data), content_type='application/json'
        )
        responses_data = json.loads(responses.content)
        self.assertEqual(responses.status_code, status.HTTP_406_NOT_ACCEPTABLE)

#*** Logout Valid Test
    def testValid_Logout(self):
        client = APIClient()
        client.force_authenticate(user=self.user1)
        responses = client.get(reverse('logout'))
        self.assertEqual(responses.status_code, status.HTTP_200_OK)

#***Logout InValid Test
    def testInValid_Logout_notAuth(self):
        client = APIClient()
        responses = client.get(reverse('logout'))
        self.assertEqual(responses.status_code, status.HTTP_403_FORBIDDEN)