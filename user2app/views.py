from django.shortcuts import render,redirect, get_object_or_404
from indexapp.models import UserProfile, Feedback, Course 
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.conf import settings
from functools import wraps
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    from vaderSentiment import SentimentIntensityAnalyzer


def user_login_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if 'user_email' not in request.session:
            return redirect('login')
        return f(request, *args, **kwargs)
    return wrap

@user_login_required
def dashboard(request):
    user_email = request.session.get('user_email')
    user_profile = UserProfile.objects.filter(email=user_email).first()
    
    all_courses_list = Course.objects.all()
    
    query = request.GET.get('q')
    
    if query:
        display_courses = Course.objects.filter(title__icontains=query)
    else:
        display_courses = Course.objects.all()

    return render(request, 'user_templates/dashboard.html', {
        'display_courses': display_courses,
        'all_courses_list': all_courses_list,
        'query': query,
        'user_profile': user_profile
    })

from django.shortcuts import render, get_object_or_404
from  indexapp.models import Course, Enrollment

@user_login_required
def courses_dashboard(request, course_id):
    # Get the specific course or return 404 if not found
    course = get_object_or_404(Course, id=course_id)
    
    # Optional: Check if user is actually enrolled
    # is_enrolled = Enrollment.objects.filter(user__user=request.user.username, course=course).exists()
    
    return render(request, 'user_templates/courses_dashboard.html', {
        'course': course
    })

# userapp/views.py
from indexapp.models import Enrollment, Course

@user_login_required
def user_courses_list(request):
    user_email = request.session.get('user_email')
    user_profile = UserProfile.objects.filter(email=user_email).first()

    all_courses = Course.objects.all()
    selected_course_id = request.GET.get('id')
    selected_course = None
    has_paid = False
    
    if selected_course_id and selected_course_id != "None" and selected_course_id != "":

        try:
            selected_course = get_object_or_404(Course, id=selected_course_id)
        except (ValueError, Course.DoesNotExist):
            selected_course = None
        
      

    return render(request, 'user_templates/user_courses_list.html', {
        'all_courses': all_courses,
        'selected_course': selected_course,
        'has_paid': has_paid ,
        'user_profile': UserProfile.objects.filter(email=request.session.get('user_email')).first()

    })


def certificates(request):
    return render(request, 'user_templates/certificates.html')

@user_login_required
def feedback(request):
    feed_id  = request.session.get('user_email')
    user = UserProfile.objects.get(email = feed_id)
    if request.method ==  "POST":
        user_msg = request.POST.get('feedback')
        rating = request.POST.get('rating')
        if not user_msg:
            messages.error(request, "Please enter a message.")
            return redirect('feedback')
        sid=SentimentIntensityAnalyzer()
        score=sid.polarity_scores(user_msg)
        if score['compound']>0 and score['compound']<=0.5:
            sentiment='positive'
        elif score['compound']>=0.5:
            sentiment='very positive'
        elif score['compound']<-0.5:
            sentiment='very negative'
        elif score['compound']<0 and score['compound']>=-0.5:
            sentiment='negative'
        else :
            sentiment='neutral'
        print(sentiment)
        user.save()
        Feedback.objects.create(user_details=user, star_feedback=user_msg, star_rating=rating)
        messages.success(request, "Thank you for your feedback!")
        return redirect('feedback')
    return render(request, 'user_templates/feedback.html', {'user_profile': user})
