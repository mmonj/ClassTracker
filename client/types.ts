export type ApiResponse<T> = {
  json: () => Promise<T>;
} & Response;

export type ApiPromise<T> = Promise<ApiResponse<T>>;

interface ReactivatedSerializationWidgetsDateTimeAttrs {
  id: string;
  disabled?: boolean;
  required?: boolean;
  placeholder?: string;
  format: string;
}

export interface DjangoFormsWidgetsDateTimeInput {
  template_name: "django/forms/widgets/datetime.html";
  name: string;
  is_hidden: boolean;
  required: boolean;
  value: string | null;
  attrs: ReactivatedSerializationWidgetsDateTimeAttrs;
  type: "text";
  tag: "django.forms.widgets.DateTimeInput";
}

export interface IHttpError {
  detail: string;
}

export type TNotFoundErrorList = string[];

export type TUseFetchResult<T> =
  | {
      ok: false;
      data: null;
      errors: string[];
    }
  | {
      ok: true;
      data: T;
      errors: string[];
    };
