from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from polls.models import Choice, Question


class PollsAPITests(APITestCase):
    fixtures = ["polls_seed.json"]

    def test_list_questions(self):
        """Verify GET /api/questions/ returns all seeded questions."""
        url = reverse("questions-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["question_text"], "How are you?")

    def test_retrieve_single_question(self):
        """Verify GET /api/questions/2/ returns the specific question."""
        url = reverse("questions-detail", args=[2])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["question_text"],
            "What is your favorite Python web development framework?",
        )

    def test_create_question(self):
        """Verify POST /api/questions/ creates a new question in the database."""
        url = reverse("questions-list")
        payload = {
            "question_text": "Which database do you prefer?",
            "pub_date": "2026-11-12T16:00:00Z",
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 3)
        self.assertEqual(response.data["id"], 3)

    def test_vote_on_choice(self):
        """Verify POST /api/choices/4/vote/ increments the vote count."""
        choice = Choice.objects.get(pk=4)
        initial_votes = choice.votes

        url = reverse("choices-vote", args=[4])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        choice.refresh_from_db()
        self.assertEqual(choice.votes, initial_votes + 1)
