from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
import random


def create_posts(start, end, user_profiles, tags):
    from app.models import Post, PostTag
    posts, post_tags = [], []
    batch_size = 5000
    
    print("Started creating posts.")
    for i in range(start, end):
        author = random.choice(user_profiles)
        post = Post(user=author, header=f'Question {i}?', description=f'Description {i}')
        posts.append(post)

        used_tags = random.sample(tags, 3)
        post_tags.extend(PostTag(post=post, tag=tag) for tag in used_tags)

        if len(posts) >= batch_size:
            Post.objects.bulk_create(posts)
            PostTag.objects.bulk_create(post_tags)
            posts.clear()
            post_tags.clear()

    Post.objects.bulk_create(posts)
    PostTag.objects.bulk_create(post_tags)
    print("Completed creating posts.")


def create_comments(start, end, user_profiles):
    from app.models import Post, Comment
    posts = list(Post.objects.all())
    comments = []
    batch_size = 5000

    print("Started creating comments.")
    for i in range(start, end):
        post = random.choice(posts)
        user = random.choice(user_profiles)
        post_comments = [Comment(user=user, post=post, is_correct=random.choice([True, False]), content=f'Comment {i}.{j}') for j in range(10)]
        comments.extend(post_comments)

        if len(comments) >= batch_size:
            Comment.objects.bulk_create(comments)
            comments.clear()

    Comment.objects.bulk_create(comments)
    print("Completed creating comments.")


def create_likes(user_profiles):
    from app.models import Post, Comment, PostLike, CommentLike
    posts = list(Post.objects.all())
    comments = list(Comment.objects.all())
    post_likes, comment_likes = [], []
    batch_size = 2000

    print("Started creating likes.")

    for user in user_profiles:
        liked_posts = set()
        liked_comments = set()
        
        while len(liked_posts) < 100:
            post = random.choice(posts)
            if post not in liked_posts:
                post_likes.append(PostLike(user=user, post=post, value=random.choice([1, -1])))
                liked_posts.add(post)

        while len(liked_comments) < 100:
            comment = random.choice(comments)
            if comment not in liked_comments:
                comment_likes.append(CommentLike(user=user, comment=comment, value=random.choice([1, -1])))
                liked_comments.add(comment)

        if len(post_likes) >= batch_size:
            PostLike.objects.bulk_create(post_likes)
            CommentLike.objects.bulk_create(comment_likes)
            post_likes.clear()
            comment_likes.clear()

    PostLike.objects.bulk_create(post_likes)
    CommentLike.objects.bulk_create(comment_likes)

    print("Completed creating likes.")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        from app.models import UserProfile, Tag
        
        ratio = options['ratio']

        if ratio < 10:
            self.stdout.write(self.style.ERROR('RATIO LESS THAN 10 IS NOT ALLOWED.'))
            """
            Это сделано для того, чтобы не было бесконечных циклов а также ошибок из-за слишком маленького количества тегов (<3).
            Если кол-во тегов (== ratio) < 3, то не получится каждому посту присвоить 3 тега.
            Если ratio < 10, то возникают бесконечные циклы, которые были созданы для предотвращения повторяющихся элементов (которые вызывают ошибки),
            но здесь, т.к. элементов очень мало, повторяющиеся элементы будут всегда, что приводит к бесконечному циклу.
            """
            exit(1)

        print("Creating users and profiles...")
        users = [User(username=f'user{i}', password=f'password{i}') for i in range(ratio)]
        User.objects.bulk_create(users)
        user_profiles = UserProfile.objects.bulk_create([UserProfile(user=user, username=user.username) for user in User.objects.all()])
        tags = Tag.objects.bulk_create([Tag(name=f'tag{i}') for i in range(ratio)])
        print("Completed creating users and profiles.")

        print("Creating posts...")
        create_posts(0, ratio * 10, user_profiles, tags)

        print("Creating comments...")
        create_comments(0, ratio * 10, user_profiles)

        print("Creating likes...")
        create_likes(user_profiles)

        self.stdout.write(self.style.SUCCESS('Database fill completed.'))
