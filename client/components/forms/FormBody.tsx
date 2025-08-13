import React from "react";

import { FieldHandler, useForm } from "@reactivated";
import { ListGroup } from "react-bootstrap";

import { FieldMap, FormLike } from "reactivated/dist/forms";

import { Field } from "./Field";

interface Props<T extends FieldMap> {
  form: FormLike<T>;
}

export function FormBody<T extends FieldMap>(props: Props<T>) {
  const form = useForm({ form: props.form });

  return (
    <>
      {form.nonFieldErrors !== null && (
        <ListGroup variant="ul" className="alert alert-danger p-3 mb-4">
          {form.nonFieldErrors.map((error, idx) => (
            <li key={idx} className="pb-1" style={{ listStyle: "none" }}>
              {error}
            </li>
          ))}
        </ListGroup>
      )}
      {Object.values(form.fields).map((field: FieldHandler, idx) => (
        <Field key={idx} field={field} />
      ))}
    </>
  );
}
