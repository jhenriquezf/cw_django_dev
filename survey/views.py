from django.http import JsonResponse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from survey.models import Question, Answer, Vote
from django.urls import reverse_lazy
from django.db.models import Count, F, IntegerField, Value, Case, When, BooleanField
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required


class QuestionListView(ListView):
    model = Question

    def get_queryset(self):
        user = self.request.user
        today = timezone.now().date()

        # Anotación para la bonificación de preguntas creadas hoy
        bonus_today = Case(
            When(created=today, then=Value(10)),
            default=Value(0),
            output_field=IntegerField()
        )

        # Queryset contruido en base con la anotación de bonificación
        queryset = Question.objects.annotate(
            answers_count=Count('answers'),
            ranking=F('answers_count') * 10 + F('likes') * 5 - F('dislikes') * 3 + bonus_today
        ).order_by('-ranking')[:20]

        # Añadir información sobre los votos y respuestas del usuario
        if user.is_authenticated:
            voted_likes = Vote.objects.filter(user=user, value='like').values_list('question_id', flat=True)
            voted_dislikes = Vote.objects.filter(user=user, value='dislike').values_list('question_id', flat=True)

            user_answers = Answer.objects.filter(
                author=user
            ).values_list('question_id', 'value')

            queryset = queryset.annotate(
                user_likes=Case(
                    When(id__in=voted_likes, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                user_dislikes=Case(
                    When(id__in=voted_dislikes, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                user_rating=Case(
                    *[When(id=question_id, then=Value(rating)) for question_id, rating in user_answers],
                    default=Value(0),
                    output_field=IntegerField()
                )
            )

        return queryset

class QuestionCreateView(CreateView):
    model = Question
    fields = ['title', 'description']
    success_url = reverse_lazy('survey:question-list')

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)


class QuestionUpdateView(UpdateView):
    model = Question
    fields = ['title', 'description']
    template_name = 'survey/question_form.html'


@login_required
def answer_question(request):
    user = request.user
    question_pk = request.POST.get('question_pk')
    value = request.POST.get('value')

    if not question_pk or value is None:
        return JsonResponse({'ok': False, 'error': 'Faltan datos para la respuesta.'})

    question = get_object_or_404(Question, pk=question_pk)

    # Busca una respuesta existente o crea una nueva
    answer, created = Answer.objects.get_or_create(
        question=question,
        author=user,
        defaults={'value': value}  # Este valor solo se usa si se crea una nueva respuesta
    )

    # Si la respuesta ya existe, actualiza su valor
    if not created:
        answer.value = value
        answer.save()

    return JsonResponse({'ok': True})

@csrf_exempt
def like_dislike_question(request):
    user = request.user
    question_pk = request.POST.get('question_pk')
    action = request.POST.get('action')

    if not user.is_authenticated:
        return JsonResponse({'ok': False, 'error': 'Usuario no autenticado'})

    if not question_pk or not action:
        return JsonResponse({'ok': False, 'error': 'Faltan datos'})

    try:
        question = Question.objects.get(pk=question_pk)
        vote, created = Vote.objects.get_or_create(user=user, question=question)

        if created or vote.value != action:
            if action == 'like':
                # Actualiza el contador de 'likes' de forma atómica
                Question.objects.filter(pk=question.pk).update(likes=F('likes') + 1)
                if vote.value == 'dislike':
                    Question.objects.filter(pk=question.pk).update(dislikes=F('dislikes') - 1)
            elif action == 'dislike':
                # Actualiza el contador de 'dislikes' de forma atómica
                Question.objects.filter(pk=question.pk).update(dislikes=F('dislikes') + 1)
                if vote.value == 'like':
                    Question.objects.filter(pk=question.pk).update(likes=F('likes') - 1)

            vote.value = action
            vote.save()

        return JsonResponse({'ok': True})
    except Question.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Pregunta no encontrada'})

