from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, QuerySet
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import Filmwork, RoleType


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self) -> QuerySet:
        return Filmwork.objects.prefetch_related('genres', 'person') \
            .values().all().annotate(genres=ArrayAgg('genres__name',
                                                     distinct=True),
                                     actors=ArrayAgg('person__full_name',
                                                     filter=Q(
                                                         personfilmwork__role__icontains=RoleType.ACTOR),
                                                     distinct=True),
                                     directors=ArrayAgg('person__full_name',
                                                        filter=Q(
                                                            personfilmwork__role__icontains=RoleType.DIRECTOR),
                                                        distinct=True),
                                     writers=ArrayAgg('person__full_name',
                                                      filter=Q(
                                                          personfilmwork__role__icontains=RoleType.WRITER),
                                                      distinct=True)
                                     )

    def render_to_response(self, context, **response_kwargs) -> JsonResponse:
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    model = Filmwork
    http_method_names = ['get']
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )
        page_num = self.request.GET.get('page', 1)
        if page_num == 'last':
            page_num = paginator.num_pages

        results = paginator.page(page_num)
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': results.previous_page_number() if results.has_previous() else None,
            'next': results.next_page_number() if results.has_next() else None,
            'results': list(results.object_list),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs) -> dict:
        movie_id = kwargs['object'].get('id')
        queryset = self.get_queryset()
        result = queryset.filter(Q(id=movie_id))
        return result.values()[0] if result else {}
