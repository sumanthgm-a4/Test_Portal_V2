from django.urls import path
from .views import *

urlpatterns = [
    path("", render_home, name="home"),
    path("login", render_login, name="login"),
    path("register", render_register, name="register"),
    path("logout", render_logout, name="logout"),
    path("tests/<str:question_name>", render_test_page, name="tests"),
    path('run-code', run_code, name='run_code'),
    path("questions", render_questions, name="questions"),
    path("delete-question/<str:question_name>", delete_question, name="delete_question"),
    path("add-question", add_question, name="add_question"),
]