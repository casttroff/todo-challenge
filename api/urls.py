from django.urls import re_path
from .views import login, signup, test_token, task_list, task_detail

urlpatterns = [
    re_path(r'^login/?$', login, name='auth-login'),
    re_path(r'^signup/?$', signup, name='auth-signup'),
    re_path(r'^test_token/?$', test_token, name='auth-test-token'),
    re_path(r'^tasks/?$', task_list, name='task-list'),
    re_path(r'^task/(?P<pk>\d+)/?$', task_detail, name='task-detail'),
]