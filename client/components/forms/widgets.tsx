import React from "react";

import {
  DjangoFormsWidgetsCheckboxInput,
  DjangoFormsWidgetsSelect,
  DjangoFormsWidgetsTextInput,
  DjangoFormsWidgetsTextarea,
  Types,
} from "reactivated/dist/generated";

import { DjangoFormsWidgetsDateTimeInput } from "@client/types";

export type CoreWidget = Types["Widget"];
type Optgroup = Types["Optgroup"];

type TInputElementType = React.ComponentProps<"input">["type"];

export function CheckboxInput(props: {
  id: string;
  name: string;
  className?: string;
  value: true | false;
  attrs?: DjangoFormsWidgetsCheckboxInput["attrs"];
  onChange: (value: boolean) => void;
}) {
  return (
    <input
      id={props.id}
      type="checkbox"
      name={props.name}
      className={props.className}
      checked={props.value}
      onChange={(event) => props.onChange(event.target.checked)}
      disabled={props.attrs?.disabled}
      required={props.attrs?.required}
      placeholder={props.attrs?.placeholder}
    />
  );
}

export function TextInput(props: {
  id: string;
  name: string;
  type: TInputElementType;
  className?: string;
  value: string | null;
  attrs?: DjangoFormsWidgetsTextInput["attrs"];
  onChange: (value: string) => void;
}) {
  return (
    <input
      id={props.id}
      type={props.type}
      name={props.name}
      className={props.className}
      value={props.value ?? ""}
      onChange={(event) => props.onChange(event.target.value)}
      disabled={props.attrs?.disabled}
      required={props.attrs?.required}
      placeholder={props.attrs?.placeholder}
      maxLength={
        props.attrs?.maxlength === undefined ? undefined : Number.parseInt(props.attrs.maxlength)
      }
    />
  );
}

export function Select(props: {
  id: string;
  name: string;
  className?: string;
  value: string | number | null;
  optgroups: Optgroup[];
  attrs?: DjangoFormsWidgetsSelect["attrs"];
  onChange: (value: string) => void;
}) {
  const { name, optgroups, value } = props;

  return (
    <select
      id={props.id}
      key={name}
      name={name}
      className={props.className}
      value={value ?? ""}
      onChange={(event) => props.onChange(event.target.value)}
      disabled={props.attrs?.disabled}
      required={props.attrs?.disabled}
    >
      {optgroups.map((optgroup) => {
        const optgroupValue = (optgroup[1][0].value ?? "").toString();
        return (
          <option key={optgroupValue} value={optgroupValue}>
            {optgroup[1][0].label}
          </option>
        );
      })}
    </select>
  );
}

export function Textarea(props: {
  id: string;
  name: string;
  className?: string;
  value: string | null;
  onChange: (value: string) => void;
  attrs?: DjangoFormsWidgetsTextarea["attrs"];
}) {
  const rows = props.attrs?.rows === undefined ? 4 : parseInt(props.attrs.rows);
  // if (rows < 10) rows = 10;

  return (
    <textarea
      id={props.id}
      name={props.name}
      className={props.className}
      value={props.value ?? ""}
      onChange={(event) => props.onChange(event.target.value)}
      disabled={props.attrs?.disabled}
      required={props.attrs?.required}
      placeholder={props.attrs?.placeholder}
      cols={props.attrs?.cols === undefined ? undefined : parseInt(props.attrs.cols)}
      rows={rows}
    />
  );
}

export function InputDateTime(props: {
  id: string;
  name: string;
  className?: string;
  value: string | null;
  attrs: DjangoFormsWidgetsDateTimeInput["attrs"];
  onChange: (value: string) => void;
}) {
  return (
    <input
      id={props.id}
      type="datetime-local"
      name={props.name}
      className={props.className}
      value={props.value ?? ""}
      onChange={(event) => props.onChange(event.target.value)}
      disabled={props.attrs.disabled}
      required={props.attrs.required}
      placeholder={props.attrs.placeholder}
    />
  );
}
