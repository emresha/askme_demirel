from django.shortcuts import render
from django.http import Http404
from askme_demirel.settings import BASE_DIR
from random import choice, randint

# Create your views here.

tags = ["Urgent", "Philosophy", "Games", "Physics", "Programming", "Common"]

questions = []
for i in range(1,30):
  questions.append({
    'title': 'title ' + str(i),
    'id': i,
    'text': 'text' + str(i),
    'tags': [choice(tags), choice(tags)],
    'likes': randint(-100, 100)
  })


def index(request):
    return render(request, "index.html", context={'questions': questions[:10]})

def hot(request):
   return render(request, "index.html", context={'questions': sorted(questions[:10],
                                    key=lambda x: x['likes'], reverse=True), 'hot': True})

def tag(request, tag_name):
    tag_questions = list(filter(lambda x: tag_name.title() in x['tags'], questions))
    if not tag_questions:
        raise Http404("Tag not found")
    return render(request, "tag.html", context={'questions': tag_questions, 'tag': tag_name})

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