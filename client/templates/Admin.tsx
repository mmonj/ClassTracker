import React from "react";

import { Context, interfaces, reverse, templates } from "@reactivated";
import { Card, ListGroup } from "react-bootstrap";

import { fetchByReactivated } from "@client/utils";

import { ButtonWithSpinner } from "@client/components/ButtonWithSpinner";
import { Navbar } from "@client/components/Navbar";
import { useFetch } from "@client/hooks/useFetch";
import { Layout } from "@client/layouts/Layout";

export function Template(props: templates.Admin) {
  const refreshTermsFetchState = useFetch<interfaces.BasicResponse>();

  const djangoContext = React.useContext(Context);

  const terms = ["fall2025", "spring2025"];

  async function handleRefreshTerms() {
    console.log("refreshing");

    const fetchCallback = () =>
      fetchByReactivated(
        reverse("course_searcher:refresh_semester_listing"),
        djangoContext.csrf_token,
        "GET"
      );

    const fetchResult = await refreshTermsFetchState.fetchData(fetchCallback);
    if (fetchResult.ok) console.log(fetchResult.data);
  }

  return (
    <Layout title="Course Searcher Admin" Navbar={Navbar}>
      <Card className="p-3">
        <Card.Title>Available Terms</Card.Title>
        <Card.Body className="p-1">
          <ListGroup as="ul" variant="flush" numbered className="mb-3 overflow-auto">
            {props.terms_available.map((term) => (
              <ListGroup.Item key={term.id}>
                {term.year} {term.name}
              </ListGroup.Item>
            ))}
          </ListGroup>

          <ButtonWithSpinner
            className="btn btn-primary"
            isLoadingState={refreshTermsFetchState.isLoading}
            hideChildren={false}
            type="button"
            size="sm"
            spinnerVariant="light"
            onClick={handleRefreshTerms}
          >
            Refresh Term listing
          </ButtonWithSpinner>
        </Card.Body>
      </Card>
    </Layout>
  );
}
