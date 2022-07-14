import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    # auto_now_add автоматически выставит дату создания записи
    created = models.DateTimeField(auto_now_add=True)
    # auto_now изменятся при каждом обновлении записи
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        # Этот параметр указывает Django, что этот класс не является представлением таблицы
        abstract = True


class UUIDMixin(models.Model):
    # Типичная модель в Django использует число в качестве id. В таких ситуациях поле не описывается в модели.
    # Вам же придётся явно объявить primary key.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    # Первым аргументом обычно идёт человекочитаемое название поля
    name = models.CharField(_('Name'), max_length=255)
    # blank=True делает поле необязательным для заполнения.
    description = models.TextField(_('Description'), null=True)

    class Meta:
        # Ваши таблицы находятся в нестандартной схеме. Это нужно указать в классе модели
        db_table = "content\".\"genre"
        # Следующие два поля отвечают за название модели в интерфейсе
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class Gender(models.TextChoices):
    MALE = 'male', _('Male')
    FEMALE = 'female', _('Female')


class RoleType(models.TextChoices):
    DIRECTOR = 'director', _('Director')
    ACTOR = 'actor', _('Actor')
    WRITER = 'writer', _('Writer')


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('Full name'), max_length=255)
    gender = models.TextField(_('Gender'), choices=Gender.choices, null=True)

    class Meta:
        db_table = "content\".\"person"

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):

    class FilmType(models.TextChoices):
        MOVIE = 'M', _('Movies')
        TV_SHOW = 'TV', _('Tv_show')

    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    creation_date = models.DateField(_('Creation date'))
    rating = models.FloatField(_('Rating'), blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(10)])
    type = models.CharField(_('Type film'), max_length=2, choices=FilmType.choices, blank=False)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    person = models.ManyToManyField(Person, through='PersonFilmwork')
    certificate = models.CharField(_('Certificate'), max_length=512, blank=True)
    # Параметр upload_to указывает, в какой подпапке будут храниться загружемые файлы.
    # Базовая папка указана в файле настроек как MEDIA_ROOT
    file_path = models.FileField(_('File'), blank=True, null=True, upload_to='movies/')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('movie')
        verbose_name_plural = _('movies')
        indexes = [
            models.Index(fields=['creation_date'],
                         name='film_work_creation_date_idx'),
        ]

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        constraints = [
            models.UniqueConstraint(
                fields=['film_work', 'genre'],
                name='genre_film_work_ids_idx')]


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.CharField(_('Role'), max_length=32, choices=RoleType.choices, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        constraints = [
            models.UniqueConstraint(
                fields=['film_work', 'person', 'role'],
                name='person_film_work_role_idx')]
