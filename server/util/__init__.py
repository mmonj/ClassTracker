from typing import Type, TypeVar

from django.db import models

T = TypeVar("T", bound=models.Model)


def bulk_create_and_get(
    model_class: Type[T],
    items: list[T],
    *,
    unique_fieldnames: list[str],
    batch_size: int | None = None,
) -> models.QuerySet[T]:
    """
    Bulk creates items in the database with ignore_conflicts=True and
    returns the full queryset of records with their primary keys populated.

    Args:
        model_class (Type[models.Model]): The Django model class.
        items (List[models.Model]): A list of model instances to be created.
        batch_size (int|None): Limit committed records to a specified batch size.
        unique_fieldnames (List[str]): The field names based on which to re-query after bulk_create and return them.

    Returns:
        QuerySet[models.Model]: The successfully inserted records with primary keys.
    """
    model_class.objects.bulk_create(items, batch_size=batch_size, ignore_conflicts=True)  # type: ignore [attr-defined]

    filter_criteria = {}
    for field in unique_fieldnames:
        filter_criteria[f"{field}__in"] = {getattr(item, field) for item in items}

    return model_class.objects.filter(**filter_criteria)  # type: ignore [no-any-return, attr-defined]
