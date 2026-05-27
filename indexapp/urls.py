from django.urls import path 
from indexapp import views
from user2app import views as user_views

urlpatterns = [
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('courses/',views.courses,name='courses'),
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('contact/',views.contact,name='contact'),
    path('portfolio/',views.portfolio,name='portfolio'),
    path('blog/',views.blog,name='blog'),
    path('blog-details/',views.blog_details,name='blog_details'),
    path('elements/',views.elements,name='elements'),
    path('main/',views.main,name='main'),
    path('otp/',views.otp,name='otp'),
    path('forget-password/', views.forget_pw, name='forget_pw'),
    path('reset-pw/<uuid:token>/', views.reset_pw, name='reset_pw'),
    path('dashboard/',user_views.dashboard,name='dashboard'),
    path('my-learning/', user_views.user_courses_list, name='user_courses_list'),
    path('course-content/<int:course_id>/', user_views.courses_dashboard, name='courses_dashboard'),
    path('certificates/', user_views.certificates, name='certificates'),
    path('feedback/', user_views.feedback, name='feedback'),
    path('download-sample/', views.download_sample_lead, name='download_sample_lead'),
    path('register-quiz/',views.register_quiz,name='register_quiz'),

]
