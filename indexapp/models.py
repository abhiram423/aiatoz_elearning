from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.CharField(max_length=50,default='')
    mobile = models.CharField(max_length=15)
    email = models.EmailField(unique=True,default='')
    password_reset_token = models.CharField(max_length=100, unique=True, blank=True, null=True)


    def __str__(self):
        return self.email

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    course_content = models.TextField(default='', blank=True)
    course_pdf = models.FileField(upload_to='course_pdfs/', null=True, blank=True)
    video_url = models.CharField(max_length=200, default="https://www.youtube.com/embed/up68UAfH0d0")

    def __str__(self):
        return self.title


# models.py
class Enrollment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    # New Field:
    order_id = models.CharField(max_length=100, blank=True, null=True) # From Payment Gateway

    def __str__(self):
        return f"{self.user.user} - {self.course.title}"

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=100)
    content = models.TextField() # This is where you put the HTML for that specific part
    order = models.IntegerField(default=0)


 
class PDFLead(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.email}"
    

# index2app/models.py

class QuizResponse(models.Model):
    # Link it to your UserProfile
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_profile.user} - {self.question}"    
    

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, default='General Inquiry')
    message = models.TextField()
    phone  = models.CharField(max_length=15, blank=True, null=True)
    sent_at =  models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    

class Blog(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email
    
class Feedback(models.Model):
    feed_id = models.AutoField(primary_key=True)
    star_feedback = models.TextField(max_length=900)
    star_rating = models.CharField(max_length=100,null=True)
    star_Date = models.DateTimeField(auto_now_add=True, null=True)
    user_details = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user_details.user} - {self.star_rating} Stars"


