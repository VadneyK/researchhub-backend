import json

from django.test import Client
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


from paper.models import Paper
from user.models import Author, University, User


class TestData:
    first_name = 'Regulus'
    last_name = 'Black'
    author_first_name = 'R. A.'
    author_last_name = 'Black'

    invalid_email = 'testuser@gmail'
    invalid_password = 'pass'
    valid_email = 'testuser@gmail.com'
    valid_password = 'ReHub940'

    university_name = 'Hogwarts'
    university_country = 'England'
    university_state = 'London'
    university_city = 'London'

    paper_title = ('Messrs Moony, Wormtail, Padfoot, and Prongs Purveyors of'
                   ' Aids to Magical Mischief-Makers are proud to present THE'
                   ' MARAUDER\'S MAP'
                   )
    paper_publish_date = '1990-10-01'


class TestHelper:
    test_data = TestData()

    def create_user(
        self,
        first_name=test_data.first_name,
        last_name=test_data.last_name,
        email=test_data.valid_email,
        password=test_data.valid_password
    ):
        return User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

    def create_random_authenticated_user(self, unique_value):
        user = self.create_random_default_user(unique_value)
        Token.objects.create(user=user)
        return user

    def create_random_default_user(self, unique_value):
        first_name = self.test_data.first_name + str(unique_value)
        last_name = self.test_data.last_name + str(unique_value)
        email = str(unique_value) + self.test_data.valid_email
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        return user

    def create_author(
        self,
        user,
        university,
        first_name=test_data.author_first_name,
        last_name=test_data.author_last_name
    ):
        return Author.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            university=university
        )

    def create_author_without_user(
        self,
        university,
        first_name=test_data.author_first_name,
        last_name=test_data.author_last_name
    ):
        return Author.objects.create(
            first_name=first_name,
            last_name=last_name,
            university=university
        )

    def create_university(
        self,
        name=test_data.university_name,
        country=test_data.university_country,
        state=test_data.university_state,
        city=test_data.university_city
    ):
        return University.objects.create(
            name=name,
            country=country,
            state=state,
            city=city
        )

    def create_paper_without_authors(
        self,
        title=test_data.paper_title
    ):
        return Paper.objects.create(
            title=title,
            paper_publish_date=self.test_data.paper_publish_date
        )


class IntegrationTestHelper(TestData):
    client = Client()

    def get_default_authenticated_client(self):
        response = self.signup_default_user()
        response_content = self.bytes_to_json(response.content)
        token = response_content.get('key')
        client = self._create_authenticated_client(token)
        return client

    def signup_default_user(self):
        url = '/auth/signup/'
        body = {
            "username": self.valid_email,
            "email": self.valid_email,
            "password1": self.valid_password,
            "password2": self.valid_password
        }
        return self.get_post_response(url, body)

    def bytes_to_json(self, data_bytes):
        data_string = data_bytes.decode('utf-8')
        json_dict = json.loads(data_string)
        return json_dict

    def get_get_response(
        self,
        path,
        query_data=None,
        follow_redirects=True,
        client=client
    ):
        """
        Returns the response of a `GET` request made by `client`.

        query_data {'param1': ['value1', 'value2'], 'param2': ['value3']}
        """
        return client.get(
            path,
            data=query_data,
            follow=follow_redirects,
            content_type='application/json'
        )

    def get_post_response(
        self,
        path,
        data,
        client=client,
        content_type='application/json',
        follow_redirects=True
    ):
        return client.post(
            path,
            data=json.dumps(data),
            follow=follow_redirects,
            content_type=content_type
        )

    def get_authenticated_get_response(
        self,
        user,
        url,
        content_type
    ):
        csrf = False

        if content_type == 'application/json':
            content_format = 'json'
        elif content_type == 'multipart/form-data':
            content_format = 'multipart'
            csrf = True

        client = APIClient(enforce_csrf_checks=csrf)
        client.force_authenticate(user=user, token=user.auth_token)
        response = client.get(url, format=content_format)
        return response

    def get_authenticated_post_response(
        self,
        user,
        url,
        data,
        content_type
    ):
        csrf = False

        if content_type == 'application/json':
            content_format = 'json'
            data = json.dumps(data)
        elif content_type == 'multipart/form-data':
            content_format = 'multipart'
            csrf = True

        client = APIClient(enforce_csrf_checks=csrf)
        client.force_authenticate(user=user, token=user.auth_token)
        response = client.post(url, data, format=content_format)
        return response

    def get_user_from_response(self, response):
        return response.wsgi_request.user

    def _create_authenticated_client(self, auth_token):
        return Client(HTTP_AUTHORIZATION=f'Token {auth_token}')
