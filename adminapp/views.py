from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.utils.datastructures import MultiValueDictKeyError
from adminapp.models import Genre, Movie
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import User
from webapp.models import ContactDb,RegistrationDb,Watchlist
from django.contrib import messages


def index_page(request):
    watchlist_count = Watchlist.objects.count()
    user_count = RegistrationDb.objects.count()
    messages_count = ContactDb.objects.count()
    return render(request, 'index.html', {
        'watchlist_count': watchlist_count,
        'user_count': user_count,
        'messages_count': messages_count,
    })

def login_page(request):
    return render(request, 'Admin_Login.html')

def admin_login(request):
    if request.method == "POST":
        un = request.POST.get('username')
        pswd = request.POST.get('password')

        if User.objects.filter(username__contains=un).exists():
            data = authenticate(username=un, password=pswd)
            if data is not None:
                login(request, data)
                request.session['username'] = un
                messages.success(request, "Admin login successful")
                return redirect('index_page')
            else:
                messages.error(request, "Incorrect password")
                return redirect(login_page)
        else:
            messages.warning(request, "Username not found")
            return redirect(login_page)

    return render(request, 'Admin_login.html')

def admin_logout(request):
    messages.info(request, "You have been logged out")
    request.session.flush()

    return redirect('admin_login')

def view_messages(request):
    data = ContactDb.objects.all()
    return render(request, "View_Message.html",{'data' : data})

def view_users(request):
    users = RegistrationDb.objects.all().order_by('-id')  
    return render(request, "View_Users.html", {'users': users})

def delete_user(request, user_id):
    RegistrationDb.objects.filter(id=user_id).delete()
    messages.success(request, "User deleted successfully")
    return redirect('view_users')

def view_watchlist(request):
    watch_items = Watchlist.objects.all().order_by('-id')
    return render(request, "View_Watchlist.html", {'watch_items': watch_items})

def delete_watchlist_item(request, item_id):
    Watchlist.objects.filter(id=item_id).delete()
    messages.success(request, "Movie deleted successfully")
    return redirect('view_watchlist')  