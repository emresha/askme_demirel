from django.shortcuts import redirect, render
from django.http import Http404
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage, PageNotAnInteger, InvalidPage
from django.contrib import auth
from django.contrib.auth.models import User
from app.models import Post, Comment, UserProfile, Tag
from django.contrib.auth.decorators import login_required
from app.forms import LoginForm, SignUpForm, QuestionForm, SettingsForm


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
            tags = form.cleaned_data['tags'].split(',')
            post = Post(user=request.user.profile, header=form.cleaned_data['title'], description=form.cleaned_data['description'])
            post.save()
            if len(tags) > 5:
                return render(request, "ask.html", context={'error': 'Too many tags', 'title': form.cleaned_data['title'], 'description': form.cleaned_data['description']})
            if len(tags) == 0:
                return render(request, "ask.html", context={'error': 'Question must have tags', 'title': form.cleaned_data['title'], 'description': form.cleaned_data['description']})
            
            for tag in tags:
                tag = tag.strip()
                if not Tag.objects.filter(name=tag).exists():
                    t = Tag(name=tag)
                    t.save()
                else:
                    t = Tag.objects.get(name=tag)
                post.tags.add(t)
            post.save()
            return redirect('question', id=post.id)
        else:
            return render(request, "ask.html", context={'error': 'Bad request', 'title': form.cleaned_data.get('title', ""), 'description': form.cleaned_data.get('description', ''), 'tags': form.cleaned_data.get('tags', '')})
    
    return render(request, "ask.html")

def login(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        next = request.GET.get('continue')
        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                auth.login(request, user)
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
            content = request.POST.get('content')
            if content:
                comment = Comment(post=post, user=request.user.profile, content=content)
                comment.save()
                last_page = return_pages_num(Comment.objects.get_comments_by_post(post), request)
                return redirect(f'/question/{id}?page={last_page}#{comment.id}')
            else:
                return redirect(f'/question/{id}')
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
            user = request.user
            user_profile = user.profile
        
            if User.objects.filter(username=form.cleaned_data['username']).exists() and form.cleaned_data['username'] != user.username:
                return render(request, "settings.html", context={'error': 'Username already in use', 'username': form.cleaned_data['username'], 'email': form.cleaned_data['email']})
            
            if User.objects.filter(email=form.cleaned_data['email']).exists() and form.cleaned_data['email'] != user.email:
                return render(request, "settings.html", context={'error': 'Email already in use', 'username': form.cleaned_data['username'], 'email': form.cleaned_data['email']})
            
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()
            user_profile.avatar = form.cleaned_data.get('picture', user_profile.avatar)
            user_profile.save()
            return redirect('settings')
        else:
            return render(request, "settings.html", context={'error': 'Bad request', 'username': form.cleaned_data.get('username', ''), 'email': form.cleaned_data.get('email', '')})
    
    return render(request, "settings.html")

@login_required(redirect_field_name='continue')
def logout(request):
    auth.logout(request)
    if request.GET.get('continue'):
        return redirect(request.GET.get('continue'))
    
    return redirect('index')