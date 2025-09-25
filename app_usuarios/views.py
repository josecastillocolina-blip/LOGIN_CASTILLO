from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from .models import PasswordResetToken
from .forms import PasswordResetRequestForm, PasswordResetConfirmForm

def contacto(request):
    redirigir = False
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        mensaje = request.POST.get("mensaje")

        # Contenido del correo
        asunto = f"Nuevo mensaje de contacto de {nombre}"
        cuerpo = f"De: {nombre} <{email}>\n\nMensaje:\n{mensaje}"

        try:
            send_mail(
                asunto,
                cuerpo,
                settings.DEFAULT_FROM_EMAIL,   # remitente
                [settings.EMAIL_HOST_USER],   # destinatario (tu mismo)
                fail_silently=False,
            )
            # aquí quitamos messages.success
            redirigir = True
            return render(request, "usuarios/contacto.html", {"redirigir": redirigir})
        except Exception as e:
            return render(request, "usuarios/contacto.html", {
                "error": f"❌ Error al enviar el mensaje: {e}"
            })

    return render(request, "usuarios/contacto.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # inicia la sesión
            return redirect("home")  # redirige al panel principal
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "usuarios/login.html")


@login_required(login_url='login')
def home(request):
    usuarios = User.objects.all()
    return render(request, "usuarios/home.html", {"usuarios": usuarios})


def logout_view(request):
    logout(request)
    return redirect("login")  # vuelve al login después de cerrar sesión


def reset_password(request):
    return render(request, "usuarios/reset_password.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validar que las contraseñas coincidan
        if password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect("register")

        # Validar que no exista el usuario
        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso")
            return redirect("register")

        # Validar que el correo no esté repetido
        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado")
            return redirect("register")

        # Crear usuario
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        messages.success(request, "Usuario creado exitosamente. Ahora inicia sesión.")
        return redirect("login")  # 👉 Después de registrarse va al login

    return render(request, "usuarios/register.html")


# -----------------------------
# CRUD de Usuarios
# -----------------------------
@login_required
def eliminar_usuario(request, user_id):
    usuario = User.objects.get(id=user_id)

    # Evitar que un usuario se elimine a sí mismo
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propio usuario.")
    else:
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")

    # 👉 Redirige siempre al panel principal
    return redirect("home")


@login_required
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        usuario.username = request.POST.get("username")
        usuario.email = request.POST.get("email")
        usuario.save()
        # Aquí el mensaje de éxito 👇
        messages.success(request, "✅ Usuario actualizado correctamente.")

        return redirect("editar_usuario", user_id=usuario.id) # redirige al panel principal

    return render(request, "usuarios/editar_usuario.html", {"usuario": usuario})

# -----------------------------
# RECUPERACIÓN DE CONTRASEÑA
# -----------------------------

def password_reset_request(request):
    """
    Vista para solicitar el restablecimiento de contraseña
    """
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                
                # Invalidar tokens anteriores del usuario
                PasswordResetToken.objects.filter(user=user).delete()
                
                # Crear nuevo token
                token = PasswordResetToken.objects.create(user=user)
                
                # Construir URL de reset (CORREGIDO para usar la URL correcta)
                reset_url = f"http://{request.get_host()}/usuarios/password-reset/{token.token}/"
                
                # Enviar email (usando la misma configuración que contacto)
                subject = 'Recuperación de contraseña - Mi Proyecto'
                message = f'''
                Hola {user.username},

                Has solicitado restablecer tu contraseña en Mi Proyecto.

                Por favor, haz clic en el siguiente enlace para crear una nueva contraseña:

                {reset_url}

                Este enlace expirará en 24 horas.

                Si no solicitaste este cambio, por favor ignora este mensaje.

                Atentamente,
                Equipo de Soporte - Mi Proyecto
                '''
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,  # Usa el mismo remitente que contacto
                        [email],
                        fail_silently=False,
                    )
                    messages.success(request, '✅ Se ha enviado un enlace de recuperación a tu correo electrónico.')
                except Exception as e:
                    messages.error(request, f'❌ Error al enviar el email: {str(e)}')
                
                return redirect('password_reset_request')
                
            except User.DoesNotExist:
                messages.error(request, '❌ No existe un usuario con este correo electrónico.')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'usuarios/password_reset_request.html', {'form': form})

def password_reset_confirm(request, token):
    """
    Vista para confirmar y establecer nueva contraseña
    """
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
        
        if not token_obj.is_valid():
            token_obj.delete()
            messages.error(request, '❌ El enlace de recuperación ha expirado.')
            return redirect('password_reset_request')
        
        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                user = token_obj.user
                password = form.cleaned_data['password']
                user.set_password(password)
                user.save()
                
                # Marcar token como usado
                token_obj.mark_as_used()
                
                messages.success(request, '✅ Contraseña restablecida correctamente. Ya puedes iniciar sesión.')
                return redirect('login')
        else:
            form = PasswordResetConfirmForm()
        
        return render(request, 'usuarios/password_reset_confirm.html', {'form': form, 'token': token})
    
    except PasswordResetToken.DoesNotExist:
        messages.error(request, '❌ El enlace de recuperación no es válido.')
        return redirect('password_reset_request')