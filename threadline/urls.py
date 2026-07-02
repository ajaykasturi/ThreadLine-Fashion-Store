# Login/logout/password-reset use Django's built-in auth views rather than
# hand-rolled ones - the reset flow (request -> email -> reset link -> new
# password) is annoying to get right and Django already does it.
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from store.forms import LoginForm, PasswordResetRequestForm, PasswordResetConfirmForm

urlpatterns = [
    path('admin/', admin.site.urls),

    # login / logout (templates live in templates/registration/)
    path('login/', auth_views.LoginView.as_view(authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # ---- forgot password (4-step built-in flow) ----
    path('password_reset/', auth_views.PasswordResetView.as_view(form_class=PasswordResetRequestForm), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(form_class=PasswordResetConfirmForm), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('', include('store.urls')),
]

# Serve uploaded media in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
