import React from "react";

import { templates } from "@reactivated";
import { Card } from "react-bootstrap";

import { Navbar } from "@client/components/Navbar";
import { Layout } from "@client/layouts/Layout";

export function Template(props: templates.AddClasses) {
  const [selectedTerm, setSelectedTerm] = React.useState("");
  const terms = ["fall2025", "spring2025"];

  return (
    <Layout title={props.title} Navbar={Navbar}>
      <Card className="p-3">
        <Card.Title>
          <h3>Refresh Classes</h3>
        </Card.Title>
        <Card.Body>
          <div className="mb-3">Refresh Classes for {selectedTerm || "No term selected"}</div>
          <select className="form-select mb-3">
            {terms.map((term, idx) => {
              return (
                <option key={idx} value={term}>
                  {term}
                </option>
              );
            })}
          </select>
          <button className="d-block btn btn-primary" type="button">
            Refresh
          </button>
        </Card.Body>
      </Card>

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
