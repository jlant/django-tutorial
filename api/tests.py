from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from polls.models import Choice, Question


class PollsAPITests(APITestCase):
    fixtures = ["polls_seed.json"]

    def test_list_questions(self):
        """Verify GET /api/questions/ returns all 3 seeded work questions."""
        url = reverse("questions-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(
            response.data[0]["question_text"],
            "Which internal web tool would be most valuable to our engineering team next?",
        )

    def test_retrieve_single_question(self):
        """Verify GET /api/questions/2/ returns the second work question."""
        url = reverse("questions-detail", args=[2])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["question_text"],
            "How do you prefer accessing internal engineering applications?",
        )

    def test_create_question(self):
        """Verify POST /api/questions/ creates a 4th question in the database."""
        url = reverse("questions-list")
        payload = {
            "question_text": "Which database do you prefer?",
            "pub_date": "2026-11-18T15:00:00Z",
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 4)
        self.assertEqual(response.data["id"], 4)

    def test_vote_on_choice(self):
        """Verify POST /api/choices/1/vote/ increments the vote count."""
        choice = Choice.objects.get(pk=1)
        initial_votes = choice.votes

        url = reverse("choices-vote", args=[1])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        choice.refresh_from_db()
        self.assertEqual(choice.votes, initial_votes + 1)
