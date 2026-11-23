from rest_framework import serializers

from polls.models import Choice, Question


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("id", "question", "choice_text", "votes")
        # Votes only change through the vote action, never by a direct write.
        read_only_fields = ("votes",)


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(source="choice_set", many=True, read_only=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "question_text",
            "pub_date",
            "was_published_recently",
            "choices",
        )
