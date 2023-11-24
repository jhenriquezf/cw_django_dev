from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone



class Question(models.Model):
    created = models.DateField('Creada', auto_now_add=True)
    author = models.ForeignKey(get_user_model(), related_name="questions", verbose_name='Pregunta',
                               on_delete=models.CASCADE)
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descripción')
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    # TODO: Quisieramos tener un ranking de la pregunta, con likes y dislikes dados por los usuarios.
    def calculate_ranking(self):
        total_answers = self.answers.count() * 10
        total_likes = self.likes * 5
        total_dislikes = self.dislikes * 3

        ranking = total_answers + total_likes - total_dislikes

        # Agrega 10 puntos si la pregunta es del día de hoy
        if self.created.date() == timezone.now().date():
            ranking += 10

        return ranking

    def get_absolute_url(self):
        return reverse('survey:question-edit', args=[self.pk])


class Answer(models.Model):
    ANSWERS_VALUES = ((0,'Sin Responder'),
                      (1,'Muy Bajo'),
                      (2,'Bajo'),
                      (3,'Regular'),
                      (4,'Alto'),
                      (5,'Muy Alto'),)

    question = models.ForeignKey(Question, related_name="answers", verbose_name='Pregunta', on_delete=models.CASCADE)
    author = models.ForeignKey(get_user_model(), related_name="answers", verbose_name='Autor', on_delete=models.CASCADE)
    value = models.PositiveIntegerField("Respuesta", default=0)
    comment = models.TextField("Comentario", default="", blank=True)

class Vote(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    VOTE_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.CharField(max_length=10, choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('user', 'question')
