from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import Http404
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage, PageNotAnInteger, InvalidPage
from django.contrib import auth
from django.contrib.auth.models import User
from app.models import Post, Comment, UserProfile
from django.contrib.auth.decorators import login_required
from app.forms import LoginForm, SignUpForm, QuestionForm, SettingsForm, CommentForm

"""
Функция пагинации
"""
def return_pages_num(objects_list, request, per_page=5):    
    p = Paginator(objects_list, per_page)
    return p.num_pages

def paginate(objects_list, request, per_page=5):
    page_num = request.GET.get('page')
        
    p = Paginator(objects_list, per_page)
    try:
        question_page = p.page(page_num)
    except (EmptyPage, PageNotAnInteger, InvalidPage) as e:
        question_page = p.page(1)
        
    return question_page

def index(request):
    # print(request.user.profile.avatar.url)
    questions = Post.objects.get_new()
    return render(request, "index.html", context={'questions': paginate(questions, request)})

def hot(request):
    hot_questions = Post.objects.get_hot()
    return render(request, "index.html", context={'questions': paginate(hot_questions, request), 'hot': True})

def tag(request, tag_name):
    tag_questions = Post.objects.get_by_tag(tag_name)
    if not tag_questions:
        raise Http404("Tag not found")
    
    return render(request, "tag.html", context={'questions': paginate(tag_questions, request), 'tag': tag_name})

@login_required(redirect_field_name='continue')
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            res = form.post(request)
            if res['error'] is None:
                return redirect('question', id=res['id'])
            else:
                return render(request, "ask.html", context={'error': res['error'], 'title': form.cleaned_data['title'], 'description': form.cleaned_data['description']})                
        else:
            return render(request, "ask.html", context={'error': 'Please fill the form out correctly.', 'title': form.cleaned_data.get('title', ""), 'description': form.cleaned_data.get('description', ''), 'tags': form.cleaned_data.get('tags', '')})
    
    return render(request, "ask.html")

def login(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        next = request.GET.get('continue') or request.POST.get('continue')
        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                auth.login(request, user)
                # print(request.GET)
                if next:
                    return redirect(next)
                return redirect('index')
            else:
                return render(request, "login.html", context={'error': 'Invalid username or password', 'login': form.cleaned_data['username']})
        else:
            return render(request, "login.html", context={'error': 'Bad request', 'login': form.cleaned_data['username']})

    return render(request, "login.html")

def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        # print(form.errors)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists() and User.objects.filter(email=form.cleaned_data['email']).exists():
                return render(request, "signup.html", context={'error': 'User already exists or email is already in use', 'username': form.cleaned_data['username'], 'email': form.cleaned_data['email']})
            
            if form.cleaned_data['password'] == form.cleaned_data['password_confirm']:
                user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password'])
                user.save()
                profile = UserProfile(user=user, avatar=form.cleaned_data.get('picture', None))
                profile.save()
                return redirect('login')
            else:
                return render(request, "signup.html", context={'error': 'Passwords do not match', 'username': form.cleaned_data['username'], 'email': form.cleaned_data['email']})
        else:
            return render(request, "signup.html", context={'error': 'Bad request', 'data': form.cleaned_data})
    
    return render(request, "signup.html")

def question(request, id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            post = Post.objects.get_by_id(id)
            form = CommentForm(request.POST)
            if form.is_valid():
                res = form.post(request, post.id)
                if res['error'] is None:
                    last_page = res['last_page']
                    comment_id = res['comment_id']
                    return redirect(f'/question/{id}?page={last_page}#{comment_id}')
            else:
                return redirect(f'/question/{id}', context={'error': 'Comment cannot be empty'})
        else:
            return redirect(f'/login?continue={request.path}')
    
    try:
        question = Post.objects.get_by_id(id)
    except Exception as e:
        raise Http404("Question not found.")
    
    comments = Comment.objects.get_comments_by_post(question)
    # print(len(comments))
    return render(request, "question.html", context={'question': question, 'id': id, 'comments': paginate(comments, request)})

@login_required(redirect_field_name='continue')
def settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES)
        # print(form.errors)
        if form.is_valid():
            res = form.change_user_data(request)
            if res['error'] is None:
                return redirect('settings')
            else:
                return render(request, "settings.html", context=res)
            
        else:
            return render(request, "settings.html", context={'error': 'Bad request', 'username': form.cleaned_data.get('username', ''), 'email': form.cleaned_data.get('email', '')})
    
    return render(request, "settings.html")

@login_required(redirect_field_name='continue')
def logout(request):
    auth.logout(request)
    if request.GET.get('continue'):
        return redirect(request.GET.get('continue'))
    
    return redirect('index')