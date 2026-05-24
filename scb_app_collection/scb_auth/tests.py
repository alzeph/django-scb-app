from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from scb_auth.models import  Group, User
from django_factory_all import ModelFactory
from scb_auth.utils import login_user_in_test
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

User = get_user_model()

class AuthsTestCase(TestCase):
    def setUp(self):
        self.factory = ModelFactory(max_depth=7, create_m2m=True)
        kwargs_user = self.factory.build_create_kwargs(User)
        kwargs_user.pop('phone_number')
        self.user = User.objects.create(phone_number='+22500000000', **kwargs_user)
        self.client = login_user_in_test(self.user)
        
    # test group 
    
    def test_retrieve_group_success(self):
        group = self.factory.create(Group)
        url = reverse('scb_auth:groups-detail', kwargs={'pk': group.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data), ReturnDict)
        
    def test_retrieve_group_failure_not_found(self):
        url = reverse('scb_auth:groups-detail', kwargs={'pk': "test"})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 404)
        
    def test_retrieve_group_failure_not_authentification(self):
        client = APIClient()
        url = reverse('scb_auth:groups-detail', kwargs={'pk': "test"})
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, 401)
        
    def test_list_group_success(self):
        self.factory.create(Group)
        self.factory.create(Group)
        url = reverse('scb_auth:groups-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, ReturnList)
        self.assertGreaterEqual(len(response.data), 2)
        
    def test_list_group_failure_not_authentification(self):
        client = APIClient()
        url = reverse('scb_auth:groups-list')
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, 401)
    
    # test user
    
    def test_create_user_success(self):
        url = reverse('scb_auth:users-list')
        response = self.client.post(url, {"phone_number": "+22500000034", "password": "1234"}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(type(response.data), ReturnDict)
    
    def test_create_user_failure_data_partial(self):
        url = reverse('scb_auth:users-list')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)
        
    def test_update_user_success(self):
        url = reverse('scb_auth:users-detail', kwargs={'pk': self.user.pk})
        response = self.client.patch(url, {'email': 'testupdate@test.com'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'testupdate@test.com')
        
    def test_update_user_failure_not_found(self):
        url = reverse('scb_auth:users-detail', kwargs={'pk': "test"})
        response = self.client.patch(url, {'email': 'testupdate@test.com'}, format='json')
        self.assertEqual(response.status_code, 404)
        
    def test_update_user_failure_not_authentificate(self):
        client = APIClient()
        url = reverse('scb_auth:users-detail', kwargs={'pk': "test"})
        response = client.patch(url, {'email': 'testupdate@test.com'}, format='json')
        self.assertEqual(response.status_code, 401)
        
    def test_list_user_success(self):
        url = reverse('scb_auth:users-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data), ReturnList)
        
    def test_list_user_failure_not_authentificate(self):
        client = APIClient()
        url = reverse('scb_auth:users-list')
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, 401)
        
    def test_retrieve_user_success(self):
        url = reverse('scb_auth:users-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data), ReturnDict)
        
    def test_retrieve_user_failure_not_authentification(self):
        client = APIClient()
        url = reverse('scb_auth:users-detail', kwargs={'pk': "test"})
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, 401)
        
    def test_retrieve_user_failure_not_found(self):
        url = reverse('scb_auth:users-detail', kwargs={'pk': "test"})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 404)
        
    def test_delete_user_sucess(self):
        kwargs_user = self.factory.build_create_kwargs(User)
        kwargs_user.pop('phone_number')
        user = User.objects.create(phone_number='+225000000023', **kwargs_user)
        url = reverse('scb_auth:users-detail', kwargs={'pk': user.pk})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 204)
        
    def test_delete_user_failure_not_found(self):
        url = reverse('scb_auth:users-detail', kwargs={'pk': "test"})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 404)
        
    def test_delete_user_failure_not_authentification(self):
        client = APIClient()
        url = reverse('scb_auth:users-detail', kwargs={'pk': "test"})
        response = client.delete(url, format='json')
        self.assertEqual(response.status_code, 401)
          
    def test_verify_email_success_email_exist(self):
        self.user.email = 'testupdate@test.com'
        self.user.save()
        self.user.refresh_from_db()
        url = reverse('scb_auth:users-verify-email')
        response = self.client.post(url, {'verify': self.user.email}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data), dict)
        self.assertTrue(response.data['exists'])
        
    def test_verify_email_success_email_not_exist(self):
        url = reverse('scb_auth:users-verify-email')
        response = self.client.post(url, {'verify': 'testupdate@test.com'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data), dict)
        self.assertFalse(response.data['exists'])   

    def test_verify_email_failure_data_not_found(self):
        url = reverse('scb_auth:users-verify-email')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)
    
    def test_verify_phone_success_phone_exist(self):
        url = reverse('scb_auth:users-verify-phone')
        response = self.client.post(url, {'verify': self.user.phone_number}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data), dict)
        self.assertTrue(response.data['exists'])
    
    def test_verify_phone_success_phone_not_exist(self):
        url = reverse('scb_auth:users-verify-phone')
        response = self.client.post(url, {'verify': '00001223'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data), dict)
        self.assertFalse(response.data['exists'])
        
    def test_verify_phone_failure_data_not_found(self):
        url = reverse('scb_auth:users-verify-phone')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)   
      
    def test_current_user_success(self):
        url = reverse('scb_auth:users-current')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data), ReturnDict)
        
    def test_current_user_failure_not_authentification(self):
        client = APIClient()
        url = reverse('scb_auth:users-current')
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, 401)
      
    def test_login_success(self):
        kwargs_user = self.factory.build_create_kwargs(User)
        kwargs_user.pop('phone_number')
        user = User.objects.create(phone_number='+225000000023', **kwargs_user)
        user.set_password('qwerty123')
        user.save()
        user.refresh_from_db()
        url = reverse('scb_auth:users-login')
        response_otp = self.client.post(reverse('scb_auth:users-obtain-otp'), {'username': user.phone_number}, format='json')
        self.assertEqual(response_otp.status_code, 200)
        response = self.client.post(url, {'username': user.phone_number, 'code': '123456'}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_login_with_register_include_otp_ask_true_success(self):
        phone_number = '+225000000023'
        url = reverse('scb_auth:users-login')
        response_otp = self.client.post(reverse('scb_auth:users-obtain-otp'), {'username': phone_number}, format='json')
        self.assertEqual(response_otp.status_code, 200)
        response = self.client.post(url, {'username': phone_number, 'code': '123456'}, format='json')
        self.assertEqual(response.status_code, 401)
    
    def test_login_failure_data_not_found(self):
        url = reverse('scb_auth:users-login')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)
        
    def test_login_failure_data_partial(self):
        kwargs_user = self.factory.build_create_kwargs(User)
        kwargs_user.pop('phone_number')
        user = User.objects.create(phone_number='+225000000023', **kwargs_user)
        user.set_password('qwerty123')
        user.save()
        user.refresh_from_db()
        url = reverse('scb_auth:users-login')
        response = self.client.post(url, {'phone_number': '+225000000023'}, format='json')
        self.assertEqual(response.status_code, 400)
    
    def test_logout_success(self):
        url = reverse('scb_auth:users-logout')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 204)
        
    def test_session_check_success(self):
        url = reverse('scb_auth:users-session-check')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data), ReturnDict)
    
    def test_session_check_not_authentification(self):
        client = APIClient()
        url = reverse('scb_auth:users-session-check')
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, 401)
        
    def test_refresh_success(self):
        url = reverse('scb_auth:users-refresh')
        response = self.client.post(url, {'refresh': self.client.cookies.get('refresh')},  format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data), dict)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
    