from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(max_length=128)
    

class SignUpForm(forms.Form):
    username = forms.CharField(max_length=32)
    email = forms.EmailField()
    password = forms.CharField(max_length=32)
    password_confirm = forms.CharField(max_length=32)
    picture = forms.ImageField(required=False)
    
    def signup(form, request) -> dict:
        from app.models import User, UserProfile
        
        if User.objects.filter(username=form.cleaned_data['username']).exists() and User.objects.filter(email=form.cleaned_data['email']).exists():
            return {'error': 'User already exists or email is already in use', 'username': form.cleaned_data['username'], 'email': form.cleaned_data['email']}
        
        if form.cleaned_data['password'] == form.cleaned_data['password_confirm']:
            user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            user.save()
            profile = UserProfile(user=user, avatar=form.cleaned_data.get('picture', None))
            profile.save()
            return {'error': None}
        else:
            return {'error': 'Passwords do not match', 'username': form.cleaned_data['username'], 'email': form.cleaned_data['email']}


class QuestionForm(forms.Form):
    title = forms.CharField(max_length=255)
    description = forms.CharField()
    tags = forms.CharField(required=True, max_length=255)
    
    def post(form, request) -> dict:
        from app.models import Post, Tag
        
        tags = form.cleaned_data['tags'].split(',')
        post = Post(user=request.user.profile, header=form.cleaned_data['title'], description=form.cleaned_data['description'])
        post.save()
        if len(tags) > 5:
            return {'error': 'Too many tags'}
        if len(tags) == 0:
            return {'error': 'Question must have tags'}

        tags = [i.lower() for i in tags]
        
        for tag in tags:
            tag = tag.strip()
            if not Tag.objects.filter(name=tag).exists():
                t = Tag(name=tag)
                t.save()
            else:
                t = Tag.objects.get(name=tag)
            post.tags.add(t)
        post.save()
        
        return {'error': None, 'id': post.id}
    
class CommentForm(forms.Form):
    content = forms.CharField()
    
    def post(form, request, question_id) -> dict:
        from app.models import Post, Comment
        from app.views import return_pages_num
        
        post = Post.objects.get(id=question_id)
        if post is None:
            return {'error': 'Question not found'}
        
        post.comments_count += 1
        post.save()
        
        comment = Comment(post=post, user=request.user.profile, content=form.cleaned_data['content'])
        comment.save()
        
        # removed request here
        return {'error': None, 'comment_id': comment.id, 'last_page': return_pages_num(Comment.objects.get_comments_by_post(post))}
    
class SettingsForm(forms.Form):
    
    username = forms.CharField(max_length=32)
    email = forms.EmailField()
    picture = forms.ImageField(required=False)
    
    def change_user_data(form, request) -> dict:
        from app.models import User
        user = request.user
        user_profile = user.profile
    
        if User.objects.filter(username=form.cleaned_data['username']).exists() and form.cleaned_data['username'] != user.username:
            return {'error': 'Username already in use', 'username': form.cleaned_data['username'], 'email': form.cleaned_data['email']}
        
        if User.objects.filter(email=form.cleaned_data['email']).exists() and form.cleaned_data['email'] != user.email:
            return {'error': 'Email already in use', 'username': form.cleaned_data['username'], 'email': form.cleaned_data['email']}
        
        user.username = form.cleaned_data['username']
        user.email = form.cleaned_data['email']
        user.save()
        if form.cleaned_data['picture'] is not None:
            user_profile.avatar = form.cleaned_data.get('picture', user_profile.avatar)
            user_profile.save()

        
        return {'error': None}    
