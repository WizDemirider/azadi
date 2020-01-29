from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.loginUser, name="login"),
    path('logout', views.logoutUser, name="logout"),
    path('signup', views.signupUser, name="signup"),
    path('home', views.home, name="home"),
    path('my-watches', views.my_watches, name="my-watches"),
    path('api/post_data/<int:token>', views.PostData.as_view(), name="post-data"),
    path('api/attack-pressed/<int:wid>', views.AttackPressed.as_view(), name="attack-pressed"),
]
