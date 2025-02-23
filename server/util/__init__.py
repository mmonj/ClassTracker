from typing import Any, Type, TypeVar

from django.db import IntegrityError, models, transaction
from django.http import JsonResponse

T = TypeVar("T", bound=models.Model)
TIsNewRecord = bool


def error_json_response(errors: list[str], *, status: int, **kwargs: Any) -> JsonResponse:
    return JsonResponse(errors, status=status, safe=False, **kwargs)


def bulk_create_and_get(
    model_class: Type[T],
    items: list[T],
    *,
    fields: list[str],
    batch_size: int | None = None,
) -> models.QuerySet[T]:
    """
    Bulk creates items in the database with ignore_conflicts=True and
    returns the full queryset of records with their primary keys populated.

    Args:
        model_class (Type[models.Model]): The Django model class.
        items (List[models.Model]): A list of model instances to be created.
        batch_size (int|None): Limit committed records to a specified batch size.
        fields (List[str]): The field names based on which to re-query after bulk_create and return them.

    Returns:
        QuerySet[models.Model]: The successfully inserted records with primary keys.
    """
    model_class.objects.bulk_create(items, batch_size=batch_size, ignore_conflicts=True)  # type: ignore [attr-defined]

    filter_criteria = _get_filter_criteria(items, fields)

    return model_class.objects.filter(**filter_criteria)  # type: ignore [no-any-return, attr-defined]


def atomic_get_or_create(instance: T, *, fields: list[str]) -> tuple[T, TIsNewRecord]:
    model_class: Type[T] = type(instance)

    try:
        with transaction.atomic():
            instance.save()
            return instance, True
    except IntegrityError:
        filter_criteria = _get_filter_criteria([instance], fields)
        return model_class.objects.get(**filter_criteria), False  # type: ignore [attr-defined]


def _get_filter_criteria(items: list[T], unique_fieldnames: list[str]) -> dict[str, Any]:
    filter_criteria = {}
    for field in unique_fieldnames:
        if "__" in field:
            *related_fields, final_field = field.split("__")
            filter_values = set()
            for item in items:
                related_obj = item
                for attr in related_fields:
                    related_obj = getattr(related_obj, attr, None)  # type: ignore [assignment]
                    if related_obj is None:
                        break
                if related_obj is not None:
                    filter_values.add(getattr(related_obj, final_field, None))
        else:
            filter_values = {getattr(item, field) for item in items}

        filter_criteria[f"{field}__in"] = filter_values
    return filter_criteria
