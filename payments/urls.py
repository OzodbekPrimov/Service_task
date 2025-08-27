from django.urls import path
from .views import FakePayView

urlpatterns = [
    path("fake/", FakePayView.as_view(), name="fake-pay"),
]