from django.urls import path
from mgr import sign_in_out
from mgr import event

urlpatterns = [

    path('event', event.dispatcher),


    path('signin', sign_in_out.signin),
    path('signout', sign_in_out.signout),

]