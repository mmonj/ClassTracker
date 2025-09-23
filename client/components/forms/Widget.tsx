/* eslint-disable @typescript-eslint/no-unnecessary-condition */
import React from "react";

import { FieldHandler } from "reactivated/dist/forms";
import { DjangoFormsWidgetsTextInput } from "reactivated/dist/generated";

import { classNames } from "@reactivated";

import { DjangoFormsWidgetsDateTimeInput } from "@client/types";

import * as widgets from "./widgets";

interface Props {
  id: string;
  field: FieldHandler<widgets.CoreWidget | DjangoFormsWidgetsDateTimeInput>;
  extraClassName?: string;
}

export function Widget({ field, id, extraClassName = "" }: Props) {
  if ("subwidgets" in field) {
    return (
      <>
        {field.subwidgets.map((subwidget) => {
          return <Widget id={subwidget.widget.attrs.id} key={subwidget.name} field={subwidget} />;
        })}
      </>
    );
  }

  if (field.tag === "django.forms.widgets.HiddenInput") {
    return <input id={id} type="hidden" name={field.name} defaultValue={field.value ?? ""} />;
  } else if (field.tag === "django.forms.widgets.CheckboxInput") {
    return (
      <widgets.CheckboxInput
        id={id}
        name={field.name}
        value={field.value}
        onChange={field.handler}
        className={classNames("form-check-input", extraClassName)}
        attrs={field.widget.attrs}
      />
    );
  } else if (field.tag === "django.forms.widgets.Textarea") {
    return (
      <widgets.Textarea
        id={id}
        name={field.name}
        value={field.value}
        onChange={field.handler}
        className={classNames("form-control", extraClassName)}
      />
    );
  } else if (
    field.tag === "django.forms.widgets.TextInput" ||
    field.tag === "django.forms.widgets.DateInput" ||
    field.tag === "django.forms.widgets.URLInput" ||
    field.tag === "django.forms.widgets.PasswordInput" ||
    field.tag === "django.forms.widgets.EmailInput" ||
    field.tag === "django.forms.widgets.TimeInput" ||
    field.tag === "django.forms.widgets.NumberInput"
  ) {
    return (
      <widgets.TextInput
        id={id}
        type={field.widget.type}
        name={field.name}
        value={field.value}
        onChange={field.handler}
        className={classNames("form-control", extraClassName)}
        attrs={field.widget.attrs as DjangoFormsWidgetsTextInput["attrs"]}
      />
    );
  } else if (field.tag === "django.forms.widgets.Select") {
    return (
      <widgets.Select
        id={id}
        name={field.name}
        value={field.value}
        optgroups={field.widget.optgroups}
        onChange={field.handler}
        className={classNames("form-select", extraClassName)}
      />
    );
  } else if (field.tag === "django.forms.widgets.ClearableFileInput") {
    return (
      <input
        id={id}
        className={classNames("form-control", extraClassName)}
        type="file"
        name={field.name}
        defaultValue={field.value ?? ""}
      />
    );
  } else if (field.tag === "django.forms.widgets.SelectMultiple") {
    return (
      <select
        id={id}
        name={field.name}
        multiple
        value={field.value}
        className={classNames("form-select", extraClassName)}
        onChange={(event) => {
          const value = Array.from(event.target.selectedOptions, (option) => option.value);
          field.handler(value);
        }}
      >
        {field.widget.optgroups.map((optgroup) => {
          const value = (optgroup[1][0].value ?? "").toString();
          return (
            <option key={value} value={value}>
              {optgroup[1][0].label}
            </option>
          );
        })}
      </select>
    );
  } else if (field.tag === "django.forms.widgets.DateTimeInput") {
    return (
      <widgets.InputDateTime
        id={id}
        name={field.name}
        value={field.value}
        onChange={field.handler}
        className={classNames("form-control", extraClassName)}
        attrs={field.widget.attrs}
      />
    );
  }

  // const exhastive: never = field;
  throw new Error("Exhausted field tag cases");
}
