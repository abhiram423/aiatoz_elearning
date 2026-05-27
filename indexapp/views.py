from django.shortcuts import render,redirect, get_object_or_404
from django.conf import settings
from .models import *
from django.contrib import messages
import random
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import PDFLead, ContactMessage
from functools import wraps
from django.shortcuts import redirect

def user_login_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if 'user_email' not in request.session:
            return redirect('login')
        return f(request, *args, **kwargs)
    return wrap

@csrf_exempt
def index(request):
    return render(request, 'main_templates/index.html')

def main(request):
    return render(request, 'main_templates/main.html',)

def about(request):
    return render(request, 'main_templates/about.html')


def courses(request):
    db_courses = Course.objects.all()
    return render(request, 'main_templates/courses.html', {'courses': db_courses})


@user_login_required
def enroll_course(request, course_id):
    course = Course.objects.get(id=course_id)
    user_email =request.session.get('user_email')
    profile = UserProfile.objects.get(email=user_email)

    Enrollment.objects.get_or_create(user=profile, course=course)
    return redirect('courses_dashboard', course_id=course.id)

@csrf_exempt
def blog(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            Blog.objects.create(email=email)
            return JsonResponse({"status": "success", "message": "Subscription added!"})
    return render(request, 'main_templates/blog.html',)

def blog_details(request):
    return render(request, 'main_templates/blog_details.html',)

def elements(request):
    return render(request, 'main_templates/elements.html',)

@csrf_exempt
def register(request):
    next_course = request.GET.get('next_course')

    if request.method == "POST":
        reg_next_course = request.POST.get('next_course_id')

        username = request.POST.get("username")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        print(username,email,mobile,password,confirm_password)

        # Basic validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect(f"/register/?next_course={reg_next_course}")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')
        
        django_user = User.objects.create_user(username=email, email=email, password=password)
        user = UserProfile.objects.create(user=username, mobile=mobile, email=email)
        user.save()


        request.session['quiz_next_course'] = reg_next_course
        request.session['quiz_user_email'] = email

        messages.success(request, "Registration successful!")
        return redirect("register_quiz")
    return render(request, "main_templates/register.html", {'next_course': next_course})


@csrf_exempt
def register_quiz(request):
    if request.method == "POST":
        email = request.session.get('quiz_user_email')
        course_id = request.session.get('quiz_next_course')
        
        try:
            user_profile = UserProfile.objects.get(email=email)
            
            data = request.POST
            QuizResponse.objects.create(user_profile=user_profile, question="Experience", answer=data.get('experience'))
            QuizResponse.objects.create(user_profile=user_profile, question="Interest", answer=data.get('interest'))
            QuizResponse.objects.create(user_profile=user_profile, question="Time", answer=data.get('time_commitment'))
            QuizResponse.objects.create(user_profile=user_profile, question="Math", answer=data.get('math_level'))
            QuizResponse.objects.create(user_profile=user_profile, question="GPU", answer=data.get('has_gpu'))
            QuizResponse.objects.create(user_profile=user_profile, question="Profession", answer=data.get('profession'))
            QuizResponse.objects.create(user_profile=user_profile, question="Industry", answer=data.get('industry'))
            QuizResponse.objects.create(user_profile=user_profile, question="Style", answer=data.get('learning_style'))
            QuizResponse.objects.create(user_profile=user_profile, question="Timeline", answer=data.get('timeline'))
            QuizResponse.objects.create(user_profile=user_profile, question="Goal", answer=data.get('final_goal'))

            if 'quiz_user_email' in request.session:
                del request.session['quiz_user_email']
            if 'quiz_next_course' in request.session:
                del request.session['quiz_next_course']

            if course_id:
                return redirect(f"/login/?next_course={course_id}")
            else:
                return redirect('login') 

        except:
            if course_id:
                return redirect(f"/login/?next_course={course_id}")
            return redirect('login') 

    return render(request, 'main_templates/register_quiz.html')

@csrf_exempt
def login(request):
    next_course = request.GET.get('next_course')

    if request.method == "POST":
        email = request.POST.get("email") 
        password = request.POST.get("password")
        
        next_course_id = request.POST.get("next_course_id")

        user = authenticate(request, username=email, password=password)

        if user is not None:

            request.session['user_email'] = user.email
            
            if next_course_id and next_course_id != "None" and next_course_id != "":
                return redirect(f"/my-learning/?id={next_course_id}")
            else:
                return redirect("dashboard")

        else:
            messages.error(request, "Invalid Email or Password.")
            return redirect("login")

    return render(request, "main_templates/login.html", {'next_course': next_course})



def otp(request):
    return render(request, 'main_templates/otp.html')

from django.core.mail import send_mail
from django.urls import reverse
import uuid

def forget_pw(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user_profile = UserProfile.objects.get(email=email)
            
            # Generate a unique token
            token = str(uuid.uuid4())
            user_profile.password_reset_token = token
            user_profile.save()

            # Create the reset link (Adjust domain for production)
            reset_link = request.build_absolute_uri(f"/reset-pw/{token}/")
            
            # Send Email
            subject = "Password Reset Request - AI A TO Z"
            message = f"Click the link below to reset your password:\n{reset_link}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            
            messages.success(request, "Reset link sent to your email!")
            return redirect('login')
            
        except UserProfile.DoesNotExist:
            messages.error(request, "Email not registered.")
            
    return render(request, 'main_templates/forget_pw.html')


def reset_pw(request, token):
    user_profile = get_object_or_404(UserProfile, password_reset_token=str(token))

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password == confirm_password:
           django_user = User.objects.get(email=user_profile.email)

           django_user.set_password(new_password)
           django_user.save()

           user_profile.password_reset_token = None
           user_profile.save()
           
           messages.success(request, "Password updated successfully!")
           return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, 'main_templates/reset_pw.html', {'token': token})

@csrf_exempt

def contact(request):
    if request.method ==  "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        subject = request.POST.get("subject")
        
        ContactMessage.objects.create(name=name, email=email, message=message, subject=subject)
        messages.success(request, 'Your message has sent successfully!')

    return render(request, 'main_templates/contact.html')

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def download_sample_lead(request):
    if request.method == "POST":
        full_name = request.POST.get("username")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")

        if full_name and email:

            PDFLead.objects.create(
                full_name=full_name,
                email=email,
                mobile=mobile
            )
            return JsonResponse({"status": "success"})

        return JsonResponse({"status": "success", "message": "Lead saved successfully"})
    
    return JsonResponse({"status": "error"}, status=400)

def portfolio(request):
    return render(request, 'main_templates/portfolio.html')

