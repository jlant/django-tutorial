from rest_framework.routers import DefaultRouter

from .views import ChoiceViewSet, QuestionViewSet

router = DefaultRouter()
router.register("questions", QuestionViewSet, basename="questions")
router.register("choices", ChoiceViewSet, basename="choices")

urlpatterns = router.urls
