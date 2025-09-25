from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),  
    path("register/", views.register, name="register"),
    path("home/", views.home, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("usuarios/eliminar/<int:user_id>/", views.eliminar_usuario, name="eliminar_usuario"),
    path("usuarios/editar/<int:user_id>/", views.editar_usuario, name="editar_usuario"),
    path("contacto/", views.contacto, name="contacto"),

    # ✅ Password reset con vistas integradas
    path("password-reset/", 
         auth_views.PasswordResetView.as_view(template_name="usuarios/reset_password.html"), 
         name="password_reset"),
    path("password-reset/done/", 
         auth_views.PasswordResetDoneView.as_view(template_name="usuarios/reset_password_done.html"), 
         name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", 
         auth_views.PasswordResetConfirmView.as_view(template_name="usuarios/password_reset_confirm.html"), 
         name="password_reset_confirm"),
    path("password-reset-complete/", 
         auth_views.PasswordResetCompleteView.as_view(template_name="usuarios/password_reset_complete.html"), 
         name="password_reset_complete"),
]
