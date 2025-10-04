from django.urls import path
from .views import top_coins, coin_history, qa

urlpatterns = [
    path("top", top_coins, name="top-coins"),
    path("coins/<int:coin_id>/history", coin_history, name="coin-history"),
    path("qa", qa, name="qa"),
]


