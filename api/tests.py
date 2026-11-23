from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from polls.models import Choice, Question


class PollsAPITests(APITestCase):
    fixtures = ["polls_seed.json"]

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="engineer", password="unused")

    def test_list_questions(self):
        """GET /api/questions/ returns every seeded question, oldest first."""
        response = self.client.get(reverse("questions-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Question.objects.count())
        self.assertEqual(
            response.data[0]["question_text"],
            Question.objects.order_by("id").first().question_text,
        )

    def test_retrieve_single_question_includes_choices(self):
        """GET /api/questions/<id>/ returns the question and its nested choices."""
        question = Question.objects.order_by("id").first()
        response = self.client.get(reverse("questions-detail", args=[question.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question_text"], question.question_text)
        self.assertEqual(len(response.data["choices"]), question.choice_set.count())

    def test_anonymous_create_is_rejected(self):
        """Anonymous clients cannot create questions."""
        before = Question.objects.count()
        payload = {"question_text": "Which database?", "pub_date": "2026-11-18T15:00:00Z"}
        response = self.client.post(reverse("questions-list"), payload, format="json")

        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
        self.assertEqual(Question.objects.count(), before)

    def test_authenticated_create_question(self):
        """A logged-in user can create a question."""
        self.client.force_authenticate(self.user)
        before = Question.objects.count()
        payload = {"question_text": "Which database?", "pub_date": "2026-11-18T15:00:00Z"}
        response = self.client.post(reverse("questions-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), before + 1)
        self.assertTrue(Question.objects.filter(pk=response.data["id"]).exists())

    def test_anonymous_vote_increments_count(self):
        """POST /api/choices/<id>/vote/ works without logging in."""
        choice = Choice.objects.order_by("id").first()
        initial_votes = choice.votes

        response = self.client.post(reverse("choices-vote", args=[choice.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        choice.refresh_from_db()
        self.assertEqual(choice.votes, initial_votes + 1)

    def test_votes_cannot_be_written_directly(self):
        """PATCHing votes is ignored; the vote action is the only way to change it."""
        self.client.force_authenticate(self.user)
        choice = Choice.objects.order_by("id").first()
        initial_votes = choice.votes

        self.client.patch(
            reverse("choices-detail", args=[choice.pk]), {"votes": 9999}, format="json"
        )

        choice.refresh_from_db()
        self.assertEqual(choice.votes, initial_votes)

    def test_filter_choices_by_non_integer_question_returns_400(self):
        """A malformed ?question= filter is a client error, not a server crash."""
        response = self.client.get(reverse("choices-list"), {"question": "abc"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
