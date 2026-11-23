import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls.models import Question


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is in the
        future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionVoteHTMXTests(TestCase):
    def test_htmx_vote_success_returns_results_partial(self):
        """
        An HTMX POST with a valid choice increments votes and returns
        the _results_partial.html snippet without the base layout.
        """
        question = create_question(question_text="Favorite color?", days=-1)
        choice = question.choice_set.create(choice_text="Blue", votes=0)

        url = reverse("polls:vote", args=(question.id,))
        response = self.client.post(
            url,
            {"choice": choice.id},
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "polls/_results_partial.html")
        self.assertTemplateNotUsed(response, "polls/base.html")
        self.assertContains(response, "1 vote")

        choice.refresh_from_db()
        self.assertEqual(choice.votes, 1)

    def test_htmx_vote_missing_choice_returns_form_partial_with_error(self):
        """
        An HTMX POST without a selected choice returns _detail_form_partial.html
        with an error alert and does not duplicate base.html.
        """
        question = create_question(question_text="Favorite color?", days=-1)
        question.choice_set.create(choice_text="Blue", votes=0)

        url = reverse("polls:vote", args=(question.id,))
        response = self.client.post(
            url,
            {},
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "polls/_detail_form_partial.html")
        self.assertTemplateNotUsed(response, "polls/base.html")
        self.assertContains(response, "You didn&#x27;t select a choice.")

    def test_standard_vote_redirects_without_htmx_header(self):
        """
        A standard non-HTMX POST still falls back to a 302 redirect to results.
        """
        question = create_question(question_text="Favorite color?", days=-1)
        choice = question.choice_set.create(choice_text="Blue", votes=0)

        url = reverse("polls:vote", args=(question.id,))
        response = self.client.post(url, {"choice": choice.id})

        self.assertRedirects(response, reverse("polls:results", args=(question.id,)))


class QuestionResultsViewTests(TestCase):
    def test_future_question_results_returns_404(self):
        """
        Results for an unpublished question are not visible.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:results", args=(future_question.id,))
        self.assertEqual(self.client.get(url).status_code, 404)


class QuestionVoteValidationTests(TestCase):
    def test_get_is_not_allowed(self):
        """
        Voting only accepts POST.
        """
        question = create_question(question_text="Favorite color?", days=-1)
        response = self.client.get(reverse("polls:vote", args=(question.id,)))
        self.assertEqual(response.status_code, 405)

    def test_non_integer_choice_shows_error_instead_of_crashing(self):
        """
        A tampered choice value is treated like a missing choice.
        """
        question = create_question(question_text="Favorite color?", days=-1)
        response = self.client.post(
            reverse("polls:vote", args=(question.id,)), {"choice": "abc"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You didn&#x27;t select a choice.")

    def test_vote_on_future_question_returns_404(self):
        """
        Unpublished questions cannot be voted on.
        """
        question = create_question(question_text="Future question.", days=5)
        choice = question.choice_set.create(choice_text="Blue", votes=0)
        response = self.client.post(
            reverse("polls:vote", args=(question.id,)), {"choice": choice.id}
        )
        self.assertEqual(response.status_code, 404)
        choice.refresh_from_db()
        self.assertEqual(choice.votes, 0)


class RootRedirectTests(TestCase):
    def test_root_url_redirects_to_polls_index(self):
        """
        Visiting the root URL '/' redirects to the polls index page.
        """
        response = self.client.get("/")
        self.assertRedirects(response, reverse("polls:index"))
