from django.shortcuts import render
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist, ViewDoesNotExist, FieldDoesNotExist
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage, PageNotAnInteger, InvalidPage
from app.models import Post, Comment
from random import choice, randint

"""
Функция пагинации
"""
def paginate(objects_list, request, per_page=5):
    page_num = request.GET.get('page')
        
    p = Paginator(objects_list, per_page)
    try:
        question_page = p.page(page_num)
    except (EmptyPage, PageNotAnInteger, InvalidPage) as e:
        question_page = p.page(1)
        
    return question_page

def index(request):
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

def ask(request):
    return render(request, "ask.html")

def login(request):
    return render(request, "login.html")

def signup(request):
    return render(request, "signup.html")

def question(request, id):
    try:
        question = Post.objects.get_by_id(id)
    except Exception as e:
        raise Http404("Question not found.")
    
    comments = Comment.objects.get_comments_by_post(question)
    # print(len(comments))
    return render(request, "question.html", context={'question': question, 'id': id, 'comments': paginate(comments, request)})

def settings(request):
    return render(request, "settings.html")
