import React from "react";

import { Context, reverse, templates } from "@reactivated";
import { Card } from "react-bootstrap";

import { fetchByReactivated } from "@client/utils";

import { Navbar } from "@client/components/Navbar";
import { Layout } from "@client/layouts/Layout";

export function Template(props: templates.AddClasses) {
  const djangoContext = React.useContext(Context);

  const terms = ["fall2025", "spring2025"];

  function handleRefreshTerms() {
    console.log("refreshing");
    fetchByReactivated(
      reverse("course_searcher:refresh_semester_listing"),
      djangoContext.csrf_token,
      "GET"
    )
      .then((resp) => {
        return resp.text();
      })
      .then((data) => {
        console.log(data);
      })
      .catch((error) => {
        console.error(error);
      });
  }

  return (
    <Layout title="Course Searcher Admin" Navbar={Navbar}>
      <Card className="p-3">
        <Card.Title>Refresh Semester listing</Card.Title>
        <Card.Body>
          <button type="button" className="btn btn-primary" onClick={handleRefreshTerms}>
            Refresh Term listing
          </button>
        </Card.Body>
      </Card>
    </Layout>
  );
}
