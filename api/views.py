from django.db.models import F
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from polls.models import Choice, Question

from .serializers import ChoiceSerializer, QuestionSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.prefetch_related("choice_set").order_by("id")
    serializer_class = QuestionSerializer


class ChoiceViewSet(viewsets.ModelViewSet):
    serializer_class = ChoiceSerializer

    def get_queryset(self):
        queryset = Choice.objects.order_by("id")
        question_id = self.request.query_params.get("question")
        if question_id is not None:
            if not question_id.isdigit():
                raise ValidationError({"question": "Must be an integer id."})
            queryset = queryset.filter(question_id=int(question_id))
        return queryset

    # Voting is open to anonymous users, matching the web UI.
    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    def vote(self, request, pk=None):
        choice = self.get_object()
        choice.votes = F("votes") + 1
        choice.save(update_fields=["votes"])
        choice.refresh_from_db()

        serializer = self.get_serializer(choice)
        return Response(serializer.data)
