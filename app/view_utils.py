from django.db.models import OuterRef, Subquery, IntegerField, BooleanField, Case, When, Value
from app.models import PostLike, CommentLike, Post

def annotate_questions(user_profile, questions) -> list:
    like_subquery = PostLike.objects.filter(
        user=user_profile,
        post=OuterRef('pk')
    ).values('value')[:1]

    questions = questions.annotate(
        like_value=Subquery(
            like_subquery,
            output_field=IntegerField()
        )
    )

    questions = questions.annotate(
        is_liked=Case(
            When(like_value__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        )
    )

    return questions

def annotate_post(post, user_profile) -> dict:
    like_subquery = PostLike.objects.filter(
        user=user_profile,
        post=post
    ).values('value')[:1]

    post = Post.objects.filter(id=post.id).annotate(
        like_value=Subquery(
            like_subquery,
            output_field=IntegerField()
        )
    ).annotate(
        is_liked=Case(
            When(like_value__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        )
    ).first()

    return post

def annotate_comments(comments, user_profile) -> list:
    like_subquery = CommentLike.objects.filter(
        user=user_profile,
        comment=OuterRef('pk')
    ).values('value')[:1]

    comments = comments.annotate(
        like_value=Subquery(
            like_subquery,
            output_field=IntegerField()
        )
    )

    comments = comments.annotate(
        is_liked=Case(
            When(like_value__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        )
    )

    return comments

def handle_question_like(user_profile, post, action) -> dict:
    post_like, _ = PostLike.objects.get_or_create(user=user_profile, post=post, defaults={'value': 0})

    if action == 'like':
        if post_like.value == 1:
            post_like.value = 0
            post.like_count -= 1
        elif post_like.value == -1:
            post_like.value = 1
            post.like_count += 2 
        else:
            post_like.value = 1
            post.like_count += 1
    elif action == 'dislike':
        if post_like.value == -1:
            post_like.value = 0
            post.like_count += 1
        elif post_like.value == 1:
            post_like.value = -1
            post.like_count -= 2
        else:
            post_like.value = -1
            post.like_count -= 1

    post_like.save()
    post.save()

    data = {
        'like_count': post.like_count,
        'like_value': post_like.value
    }
    
    return data

def handle_comment_like(user_profile, comment, action) -> dict:
    comment_like, _ = CommentLike.objects.get_or_create(user=user_profile, comment=comment, defaults={'value': 0})

    if action == 'like':
        if comment_like.value == 1:
            comment_like.value = 0
            comment.like_count -= 1
        elif comment_like.value == -1:
            comment_like.value = 1
            comment.like_count += 2 
        else:
            comment_like.value = 1
            comment.like_count += 1
    elif action == 'dislike':
        if comment_like.value == -1:
            comment_like.value = 0
            comment.like_count += 1
        elif comment_like.value == 1:
            comment_like.value = -1
            comment.like_count -= 2
        else:
            comment_like.value = -1
            comment.like_count -= 1

    comment_like.save()
    comment.save()

    data = {
        'like_count': comment.like_count,
        'like_value': comment_like.value
    }

    return data
