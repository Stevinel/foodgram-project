from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name="follower",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name="following",    
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_follow"
            )
        ]

    def __str__(self):
        return f"follower: {self.user.username}, following:{self.author.username}"