from django.shortcuts import render
from django.http import Http404
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage, PageNotAnInteger, InvalidPage
from random import choice, randint

tags = ["Urgent", "Philosophy", "Games", "Physics", "Programming", "Common"]

questions = []
for i in range(1,100):
  questions.append({
    'title': 'title ' + str(i),
    'id': i,
    'text': 'text' + str(i),
    'tags': [choice(tags), choice(tags)],
    'likes': randint(-100, 100)
  })

"""
Функция пагинации
"""
def paginate(objects_list, request, per_page=5):
    try:
        page_num = request.GET.get('page')
        if not page_num:
            page_num = 1
        else:
            page_num = int(page_num)
    except ValueError:
        page_num = 1
        
    p = Paginator(objects_list, per_page)
    try:
        question_page = p.page(page_num)
    except (EmptyPage, PageNotAnInteger, InvalidPage) as e:
        question_page = p.page(1)
        
    return question_page

def index(request):
    return render(request, "index.html", context={'questions': paginate(questions, request)})

def hot(request):
    hot_questions = sorted(questions, key=lambda x: x['likes'], reverse=True)
    return render(request, "index.html", context={'questions': paginate(hot_questions, request), 'hot': True})

def tag(request, tag_name):
    tag_questions = list(filter(lambda x: tag_name.title() in x['tags'], questions))
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
        question = questions[id - 1]
    except IndexError:
        raise Http404("Question not found.")
    return render(request, "question.html", context={'question': question, 'id': id})

def settings(request):
    return render(request, "settings.html")
