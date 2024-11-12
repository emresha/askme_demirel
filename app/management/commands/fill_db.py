from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
# from app.models import Post, Comment, UserProfile, Tag, PostLike, CommentLike, PostTag
import random
from multiprocessing import Pool, current_process

"""
Заполнение базы данных.
Честно говоря, мне стыдно говорить сколько я с этим мучился.
Зато работает теперь достаточно быстро и при этом не сильно загружает оперативную память.
"""

def create_posts(start, end, user_profiles, tags):
    from app.models import Post, PostTag
    posts, post_tags = [], []
    batch_size = 5000

    print(f"Process {current_process().name} started creating posts.")
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
    print(f"Process {current_process().name} completed creating posts.")

def create_comments(start, end, user_profiles):
    from app.models import Post, Comment
    posts = list(Post.objects.all())
    comments = []
    batch_size = 5000

    print(f"Process {current_process().name} started creating comments.")
    for i in range(start, end):
        post = random.choice(posts)
        user = random.choice(user_profiles)
        post_comments = [Comment(user=user, post=post, content=f'Comment {i}.{j}') for j in range(10)]
        comments.extend(post_comments)

        if len(comments) >= batch_size:
            Comment.objects.bulk_create(comments)
            comments.clear()

    Comment.objects.bulk_create(comments)
    print(f"Process {current_process().name} completed creating comments.")

def create_likes(user_profiles):
    from app.models import Post, Comment, PostLike, CommentLike
    posts = list(Post.objects.all())
    comments = list(Comment.objects.all())
    post_likes, comment_likes = [], []
    batch_size = 2000

    print(f"Process {current_process().name} started creating likes.")

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
            with transaction.atomic():
                PostLike.objects.bulk_create(post_likes)
                CommentLike.objects.bulk_create(comment_likes)
            post_likes.clear()
            comment_likes.clear()

    with transaction.atomic():
        PostLike.objects.bulk_create(post_likes)
        CommentLike.objects.bulk_create(comment_likes)

    print(f"Process {current_process().name} completed creating likes.")



class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)
        parser.add_argument('--num-processes', type=int, default=1) # можно распараллелить, по желанию, не гарантирую, что работает всегда

    def handle(self, *args, **options):
        from app.models import UserProfile, Tag
        
        ratio = options['ratio']
        num_processes = options['num_processes']

        users = [User(username=f'user{i}', password=f'password{i}') for i in range(ratio)]
        User.objects.bulk_create(users)
        user_profiles = UserProfile.objects.bulk_create([UserProfile(user=user, username=user.username) for user in User.objects.all()])
        tags = Tag.objects.bulk_create([Tag(name=f'tag{i}') for i in range(ratio)])

        chunk_size = (ratio * 10) // num_processes

        post_chunks = [(i * chunk_size, (i + 1) * chunk_size, user_profiles, tags) for i in range(num_processes)]
        with Pool(processes=num_processes) as pool:
            pool.starmap(create_posts, post_chunks)

        comment_chunks = [(i * chunk_size, (i + 1) * chunk_size, user_profiles) for i in range(num_processes)]
        with Pool(processes=num_processes) as pool:
            pool.starmap(create_comments, comment_chunks)

        user_chunks = [user_profiles[i::num_processes] for i in range(num_processes)]
        with Pool(processes=num_processes) as pool:
            pool.map(create_likes, user_chunks)


        self.stdout.write(self.style.SUCCESS('Database fill completed.'))
