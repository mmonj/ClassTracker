from typing import Type, TypeVar

from django.db import models

T = TypeVar("T", bound=models.Model)


def bulk_create_and_get(
    model_class: Type[T], items: list[T], *, unique_fieldname: str, batch_size: int | None = None
) -> models.QuerySet[T]:
    """
    Bulk creates items in the database with ignore_conflicts=True and
    returns the full queryset of records with their primary keys populated.

    Args:
        model_class (Type[models.Model]): The Django model class.
        items (List[models.Model]): A list of model instances to be created.
        batch_size (int|None): Limit commited records to a specified batch size
        unique_fieldname (str): The field name based on which to re-query after bulk_create and return them

    Returns:
        List[models.Model]: The successfully inserted records with primary keys.
    """
    # Perform bulk insert with conflict ignoring
    model_class.objects.bulk_create(items, batch_size=batch_size, ignore_conflicts=True)  # type: ignore [attr-defined]

    # Retrieve the successfully inserted records by filtering using the unique field
    unique_values = [getattr(item, unique_fieldname) for item in items]
    return model_class.objects.filter(**{f"{unique_fieldname}__in": unique_values})  # type: ignore [no-any-return, attr-defined]
