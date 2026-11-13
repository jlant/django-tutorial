from django.db.models import F
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from polls.models import Choice, Question

from .serializers import ChoiceSerializer, QuestionSerializer

"""
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
"""


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.prefetch_related("choice_set").all()
    serializer_class = QuestionSerializer


class ChoiceViewSet(viewsets.ModelViewSet):
    serializer_class = ChoiceSerializer

    def get_queryset(self):
        queryset = Choice.objects.all()
        question_id = self.request.query_params.get("question")
        if question_id is not None:
            queryset = queryset.filter(question_id=question_id)
        return queryset

    @action(detail=True, methods=["post"])
    def vote(self, request, pk=None):
        choice = self.get_object()
        choice.votes = F("votes") + 1
        choice.save(update_fields=["votes"])
        choice.refresh_from_db()

        serializer = self.get_serializer(choice)
        return Response(serializer.data)
