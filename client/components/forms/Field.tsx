import React from "react";

import { FieldHandler } from "@reactivated";

import classNames from "classnames";

import { Widget } from "./Widget";

interface Props {
  field: FieldHandler;
}

export function Field({ field }: Props) {
  const isCheckboxInput = (field.tag as string) === "django.forms.widgets.CheckboxInput";
  // @ts-expect-error [field tag types are generated on demand]
  const isHidden = field.tag === "django.forms.widgets.HiddenInput";

  return (
    <fieldset className={classNames("mb-3", { "visually-hidden": isHidden })}>
      {!isCheckboxInput && (
        <label htmlFor={field.widget.attrs.id} className="form-label">
          {field.label}
        </label>
      )}
      <Widget
        field={field}
        id={field.widget.attrs.id}
        extraClassName={classNames("mb-1", { "is-invalid": field.error !== null })}
      />
      {isCheckboxInput && (
        <label htmlFor={field.widget.attrs.id} className="form-label ms-2">
          {field.label}
        </label>
      )}

      {field.help_text !== "" && <div className="form-text">{field.help_text}</div>}

      {field.error !== null && (
        <>
          <div className="invalid-feedback ms-1">{field.error}</div>
        </>
      )}
    </fieldset>
  );
}
