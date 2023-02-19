from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from vendor.forms import VendorForm
from .utils import detectUser, send_verification_email, send_password_reset_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from vendor.models import Vendor



# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

# Restrict the vendor from accessing the customer page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied



# Create your views here.
def register(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in...')
        return redirect('myAccount')
    elif request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            # Create user using the form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()
            
            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,email=email, password=password)
            user.role = User.CUSTOMER
            user.save()
            
            # Send verification email
            send_verification_email(request, user)
            messages.success(request, "Your account has been registered succesfully!  ")
            return redirect('login')
    else:
        form = UserForm()
    context = {
        'form':form,
    }
    return render(request, 'accounts/register.html', context)

def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in...')
        return redirect('myAccount')
    if request.method == 'POST':
        #store data and create user
        form = UserForm(request.POST, request.FILES)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            
            # Send verification email
            send_verification_email(request, user)
            messages.success(request, "Your account has been registered. Please wait for the approval.")
            redirect('registerVendor')
        else:
            print("Invalid Form")
            print(form.errors)
            print(v_form.errors)
    else:
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)    
    
    context={
        'form':form,
        'v_form':v_form
    }
    return render(request, 'accounts/registerVendor.html', context)

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in...')
        return redirect('myAccount')
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email is None or password is None:
            messages.warning(request, 'Please enter both your email and password')
            return redirect('login')

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('myAccount')
        else:
            messages.warning(request, 'Invalid email or password')
            return redirect('login')

    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out')
    return redirect('login')



@login_required(login_url='login')
def myAccount(request):
    user = request.user
    if user.is_authenticated:
        redirectUrl = detectUser(user)
        return redirect(redirectUrl)
    else:
        return redirect('login') # or whatever login url you have set up

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render(request, 'accounts/custDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):

    return render(request, 'accounts/vendorDashboard.html')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active=True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('myAccount')
    
    else:
        messages.warning(request, 'Invalid activation link')
        return redirect('myAccount')
    
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.warning(request, 'This email address is not associated with any account.')
            return redirect('forgot_password')

        # Send reset password email
        try:
            send_password_reset_email(request, user)
        except Exception as e:
            messages.warning(request, f"There was an error sending the reset password email: {e}")
            return redirect('forgot_password')

        messages.success(request, 'An email has been sent with instructions for resetting your password.')
        return redirect('login')

    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    # Validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Reset your password")
        return redirect('reset_password')
    else:
        messages.warning(request,"This link has been expired")
        return redirect('myAccount')
        

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset succesfully')
            return redirect('login')
        else:
            messages.warning(request, 'Password does not macth!')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')