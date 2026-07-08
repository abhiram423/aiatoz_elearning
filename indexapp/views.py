from django.shortcuts import render,redirect, get_object_or_404
from django.conf import settings
from .models import *
from django.contrib import messages
import random, uuid
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from .models import UserProfile, QuizResponse, Course
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import PDFLead, ContactMessage
from functools import wraps
from django.shortcuts import redirect
from django.core.mail import send_mail

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
    course = get_object_or_404(Course, id=course_id)
    user_email = request.session.get('user_email')
    profile = UserProfile.objects.filter(email=user_email).first()
    
    if not profile:
        messages.error(request, "Profile not found. Please log in again.")
        return redirect('login')
        
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
    next_course = request.GET.get('next_course') or request.POST.get('next_course_id')

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        print(username,email,mobile,password,confirm_password)

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect(f"/register/?next_course={next_course}" if next_course else 'register')

        if User.objects.filter(email=email).exists() or UserProfile.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect(f"/register/?next_course={next_course}" if next_course else 'register') 
               
        django_user = User.objects.create_user(username=email, email=email, password=password)
        UserProfile.objects.create(user=django_user, name=username, mobile=mobile, email=email)


        request.session['quiz_next_course'] = next_course
        request.session['quiz_user_email'] = email

        messages.success(request, "Registration successful!")
        return redirect("register_quiz")
    
    return render(request, "main_templates/register.html", {'next_course': next_course})


@csrf_exempt
def register_quiz(request):
    email = request.session.get('quiz_user_email')
    course_id = request.session.get('quiz_next_course')
    
    if not email:
        return redirect('login')

    if request.method == "POST":
        user_profile = UserProfile.objects.filter(email=email).first()
        
        if user_profile:
            data = request.POST
            questions = ["Experience", "Interest", "Time", "Math", "GPU", "Profession", "Industry", "Style", "Timeline", "Goal"]
            fields = ['experience', 'interest', 'time_commitment', 'math_level', 'has_gpu', 'profession', 'industry', 'learning_style', 'timeline', 'final_goal']
            
            for q, f in zip(questions, fields):
                QuizResponse.objects.create(user_profile=user_profile, question=q, answer=data.get(f, ''))

        # Clean session storage safely
        request.session.pop('quiz_user_email', None)
        request.session.pop('quiz_next_course', None)

        messages.success(request, "Account fully setup! Welcome aboard.")
        return redirect(f"/login/?next_course={course_id}" if course_id else 'login')

    return render(request, 'main_templates/register_quiz.html')

@csrf_exempt
def login(request):
    next_course = request.GET.get('next_course') or request.POST.get('next_course_id')

    if request.method == "POST":
        email = request.POST.get("email") 
        password = request.POST.get("password")
        
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Check if their custom user profile actually exists in the database
            profile_exists = UserProfile.objects.filter(email=user.email).exists()
            if not profile_exists:
                # Re-create profile on the fly if it's an orphaned account
                UserProfile.objects.create(user=user, name=user.username, mobile="N/A", email=user.email)

            auth_login(request, user)
            request.session['user_email'] = user.email
            
            if next_course and next_course != "None":
                return redirect(f"/my-learning/?id={next_course}")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid Email or Password.")
            return redirect(f"/login/?next_course={next_course}" if next_course else 'login')
        
    return render(request, "main_templates/login.html", {'next_course': next_course})


def otp(request):
    return render(request, 'main_templates/otp.html')

from django.core.mail import send_mail
from django.urls import reverse
import uuid
def forget_pw(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user_profile = UserProfile.objects.filter(email=email).first()
        
        if user_profile:
            token = str(uuid.uuid4())
            user_profile.password_reset_token = token
            user_profile.save()

            reset_link = request.build_absolute_uri(f"/reset-pw/{token}/")
            
            subject = "Password Reset Request - AI A TO Z"
            message = f"Click the link below to reset your password:\n{reset_link}"
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
                messages.success(request, "Reset link sent to your email!")
                return redirect('login')
            except Exception:
                messages.error(request, "Failed to send email. Please check your SMTP connection.")
        else:
            messages.error(request, "Email not registered.")
            
    return render(request, 'main_templates/forget_pw.html')


def reset_pw(request, token):
    user_profile = get_object_or_404(UserProfile, password_reset_token=str(token))

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password == confirm_password:
           django_user = user_profile.user
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

def payment_success_callback(request):
    payment_id =  request.GET.get('payment_id')
    order_id = request.GET.get('order_id')
    course_id = request.GET.get('course_id')

    user_email = request.session.get('user_email')
    user_profile = UserProfile.objects.filter(email=user_email).first()
    course = get_object_or_404(Course, id=course_id)

    Enrollment.objects.get_or_create(
        user=user_profile,
        course=course,
        defaults={'order_id': order_id}
    )

    messages.success(request, f"Payment successful! You are now enrolled in {course.title} Successfully.")
    return redirect('courses_dashboard', course_id=course.id)


def privacy(request):
    return render(request, 'main_templates/privacy.html')

def support(request):
    return render(request, 'main_templates/support.html')

def terms(request):
    return render(request, 'main_templates/terms.html')
