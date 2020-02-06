from django.urls import path
from . import views
import django_twilio

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.loginUser, name="login"),
    path('logout', views.logoutUser, name="logout"),
    path('signup', views.signupUser, name="signup"),
    path('my-watches', views.my_watches, name="my-watches"),
    path('full-data/<int:wid>', views.fullData, name="full-data"),
    path('api/post_data/<int:token>', views.PostData.as_view(), name="post-data"),
    path('api/attack-pressed/<int:wid>', views.AttackPressed.as_view(), name="attack-pressed"),
    # path('sms', django_twilio.views.message, {
    #     'message': 'Buddha gir gaya!',
    #     'to': '+919870930069',
    #     'sender': '+918779677344'
    # }),
]
