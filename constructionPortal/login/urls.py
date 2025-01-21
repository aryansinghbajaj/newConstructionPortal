from django.urls import path
from . import views
urlpatterns =[
  path('',views.home,name='home'),
  path('register/',views.register,name='register'),
  path('login/',views.user_login,name='new_user_login'),
  path('create-project/', views.create_project, name='create-project'),
  path('open-project/', views.open_project, name='open-project'),
  path('dashboard/<str:project_id>/', views.dashboard, name='dashboard'),
  path('portal/', views.portal_view, name='portal'),
  path('materials-resources/<str:project_id>/', views.materials_resources_view, name='materials_resources'),
  path('project-completion/<str:project_id>/', views.project_completion_view, name='project_completion'),
  path('work-execution/<str:project_id>/', views.work_execution_view, name='work_execution'),
  path('billing/<str:project_id>/', views.billing_view, name='billing'),
  path('delete-project/', views.delete_project, name='delete-project'),
  path('confirm-delete/', views.confirm_delete, name='confirm-delete'),
]