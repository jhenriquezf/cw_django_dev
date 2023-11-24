from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Question, Answer, Vote
from django.urls import reverse

User = get_user_model()

class QuestionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.question = Question.objects.create(
            title='Test Question', description='Test Description', author=self.user
        )

    def test_question_creation(self):
        self.assertEqual(self.question.title, 'Test Question')

    def test_question_list_view(self):
        response = self.client.get(reverse('survey:question-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Question')

class LikeDislikeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.question = Question.objects.create(
            title='Test Question', description='Test Description', author=self.user
        )

    def test_like_question(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('survey:question-like'), {'question_pk': self.question.pk, 'action': 'like'})
        self.assertEqual(response.status_code, 200)

        updated_question = Question.objects.get(pk=self.question.pk)
        self.assertEqual(updated_question.likes, 1)

class AnswerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.question = Question.objects.create(
            title='Test Question', description='Test Description', author=self.user
        )

    def test_answer_question(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('survey:question-answer'), {'question_pk': self.question.pk, 'value': 5})
        self.assertEqual(response.status_code, 200)

        answer = Answer.objects.get(question=self.question, author=self.user)
        self.assertEqual(answer.value, 5)

