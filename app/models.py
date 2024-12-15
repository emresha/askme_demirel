from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='uploads/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class PostManager(models.Manager):
    def get_new(self):
        return self.order_by('-created_at')
    
    def get_hot(self):
        return self.order_by('-like_count')
    
    def get_by_tag(self, tag):
        return self.filter(tags__name=tag)
    
    def get_by_id(self, id):
        return self.get(id=id)
        

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='posts')
    like_count = models.IntegerField(default=1)
    comments_count = models.IntegerField(default=0)
    description = models.TextField()
    header = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, through='PostTag', related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostManager()

    def __str__(self):
        return self.header

class PostLike(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField(choices=[(1, 'Like'), (-1, 'Dislike')], default=1)

    class Meta:
        unique_together = ('user', 'post')
        
    def __str__(self):
        return f"{self.user.username} liked {self.post.header}"

class CommentManager(models.Manager):
    def get_comments_by_post(self, post):
        return self.filter(post=post).order_by('created_at')

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    is_correct = models.BooleanField(default=False)
    like_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CommentManager()

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.header}"

class CommentLike(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comment_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField(choices=[(1, 'Like'), (-1, 'Dislike')], default=1)

    class Meta:
        unique_together = ('user', 'comment')
        
    def __str__(self):
        return f"{self.user.username} liked {self.comment.post.header}'s answer"

class PostTag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('post', 'tag')
        
    def __str__(self):
        return f"{self.post.header} tagged with {self.tag.name}"
