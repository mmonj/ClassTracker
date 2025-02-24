import React from "react";

import { Context, templates } from "@reactivated";
import { Card } from "react-bootstrap";

import { Navbar } from "@client/components/Navbar";
import { useFetch } from "@client/hooks/useFetch";
import { Layout } from "@client/layouts/Layout";

export function Template(props: templates.TrackerAddClasses) {
  const refreshClassesFetchState = useFetch();
  const djangoContext = React.useContext(Context);

  const selectedTermRef = React.useRef<HTMLSelectElement | null>(null);

  return (
    <Layout title={props.title} Navbar={Navbar}>
      <Card>
        <Card.Title className="p-3">
          <h3>Add classes</h3>
        </Card.Title>
        <Card.Body>
          <button className="d-block btn btn-primary" type="button">
            Add New Person
          </button>
          <div>list of person data, searchable</div>

          <div className="my-2 p-2">
            <label htmlFor="examplePerson1" className="form-label">
              Person1
            </label>
            <input type="text" className="form-control" id="examplePerson1" />
          </div>
          <div className="my-2 p-2">
            <div>List of watched classes</div>
            <label htmlFor="exampleSearch1" className="form-label">
              Add New class (search text input, ajax)
            </label>
            <input type="text" className="form-control" id="exampleSearch1" />
          </div>
        </Card.Body>
      </Card>
    </Layout>
  );
}
