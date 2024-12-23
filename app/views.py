from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import Http404, JsonResponse
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage, PageNotAnInteger, InvalidPage
from django.contrib import auth
from django.contrib.auth.models import User
from app.models import CommentLike, Post, Comment, UserProfile, PostLike
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from app.forms import LoginForm, SignUpForm, QuestionForm, SettingsForm, CommentForm
from django.shortcuts import render, redirect, get_object_or_404
from app.view_utils import annotate_questions, annotate_post, annotate_comments, handle_question_like, handle_comment_like


"""
Функция пагинации
"""
def return_pages_num(objects_list, per_page=5):    
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

@require_POST
@login_required
def mark_correct(request):
    comment_id = request.POST.get('comment_id')
    post_id = request.POST.get('post_id')

    if not comment_id or not post_id:
        return JsonResponse({'error': 'Invalid parameters.'}, status=400)

    try:
        comment = Comment.objects.get(id=comment_id)
        post = Post.objects.get(id=post_id)
    except (Comment.DoesNotExist, Post.DoesNotExist):
        return JsonResponse({'error': 'Comment or post not found.'}, status=404)

    if post.user != request.user.profile:
        return JsonResponse({'error': 'You are not the author of this post.'}, status=403)

    if comment.post != post:
        return JsonResponse({'error': 'Comment does not belong to this post.'}, status=400)

    comment.is_correct = not comment.is_correct
    comment.save()

    return JsonResponse({'correct': comment.is_correct})

@require_POST
@login_required
def toggle_question_like(request):
    post_id = request.POST.get('post_id')
    action = request.POST.get('action')

    if not post_id or action not in ['like', 'dislike']:
        return JsonResponse({'error': 'Invalid parameters.'}, status=400)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found.'}, status=404)

    user_profile = request.user.profile

    data = handle_question_like(user_profile, post, action)

    return JsonResponse(data)

@require_POST
@login_required
def toggle_comment_like(request):
    comment_id = request.POST.get('comment_id')
    action = request.POST.get('action')

    if not comment_id or action not in ['like', 'dislike']:
        return JsonResponse({'error': 'Invalid parameters.'}, status=400)

    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'Comment not found.'}, status=404)

    user_profile = request.user.profile

    data = handle_comment_like(user_profile, comment, action)

    return JsonResponse(data)

def index(request):
    questions = Post.objects.get_new()

    if request.user.is_authenticated:
        user_profile = request.user.profile

        questions = annotate_questions(user_profile, questions)
    
    paginated_questions = paginate(questions, request)

    return render(request, "index.html", context={'questions': paginated_questions})


def hot(request):
    hot_questions = Post.objects.get_hot()
    
    if request.user.is_authenticated:
        user_profile = request.user.profile

        hot_questions = annotate_questions(user_profile, hot_questions)
        
    return render(request, "index.html", context={'questions': paginate(hot_questions, request), 'hot': True})

def tag(request, tag_name):
    tag_questions = Post.objects.get_by_tag(tag_name)
    if not tag_questions:
        raise Http404("Tag not found")
    
    if request.user.is_authenticated:
        user_profile = request.user.profile

        tag_questions = annotate_questions(user_profile, tag_questions)
    
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
        if form.is_valid():
            res = form.signup(request)
            if res['error'] is None:
                return redirect('login')
            else:
                return render(request, "signup.html", context=res)
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
        post = Post.objects.get_by_id(id)
    except Exception as e:
        raise Http404("Question not found.")
    
    comments = Comment.objects.get_comments_by_post(post)
    
    if request.user.is_authenticated:
        post = annotate_post(post, request.user.profile)
        comments = annotate_comments(comments, request.user.profile)
        
        is_author = str(request.user) == str(post.user)
        
        return render(request, "question.html", context={'question': post, 'id': id, 'comments': paginate(comments, request), 'is_author': is_author})
    else:
        return render(request, "question.html", context={'question': post, 'id': id, 'comments': paginate(comments, request)})


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