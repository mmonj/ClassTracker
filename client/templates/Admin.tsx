import React from "react";

import { Context, interfaces, reverse, templates } from "@reactivated";
import { Card, ListGroup } from "react-bootstrap";

import { fetchByReactivated } from "@client/utils";

import { ButtonWithSpinner } from "@client/components/ButtonWithSpinner";
import { Navbar } from "@client/components/Navbar";
import { useFetch } from "@client/hooks/useFetch";
import { Layout } from "@client/layouts/Layout";

export function Template(props: templates.Admin) {
  const [selectedTerm, setSelectedTerm] = React.useState(props.terms_available.at(0));
  const [selectedSchool, setSelectedSchool] = React.useState(props.schools.at(0));

  const refreshTermsFetchState = useFetch<interfaces.BasicResponse>();
  const refreshSubjectsFetchState = useFetch<interfaces.BasicResponse>();
  const refreshClassesFetchState = useFetch<interfaces.BasicResponse>();

  const djangoContext = React.useContext(Context);

  const isAnyFetcherLoading =
    refreshTermsFetchState.isLoading ||
    refreshSubjectsFetchState.isLoading ||
    refreshClassesFetchState.isLoading;

  async function handleRefreshTerms() {
    const fetchCallback = () =>
      fetchByReactivated(
        reverse("course_searcher:refresh_available_terms"),
        djangoContext.csrf_token,
        "POST"
      );

    const fetchResult = await refreshTermsFetchState.fetchData(fetchCallback);
    if (fetchResult.ok) window.location.reload();

    console.log(fetchResult.data);
  }

  async function handleRefreshSubjectsData() {
    if (selectedSchool === undefined || selectedTerm === undefined) {
      console.error("No school or term exists");
      return;
    }

    const callback = () =>
      fetchByReactivated(
        reverse("course_searcher:refresh_semester_data", {
          school_id: selectedSchool.id,
          term_id: selectedTerm.id,
        }),
        djangoContext.csrf_token,
        "POST"
      );

    const result = await refreshSubjectsFetchState.fetchData(callback);
    if (result.ok) console.log(result.data);
  }

  async function handleRefreshClassesData(subjectId: number) {
    if (selectedSchool === undefined || selectedTerm === undefined) {
      console.error("No school or term exists");
      return;
    }

    const callback = () =>
      fetchByReactivated(
        reverse("course_searcher:refresh_class_data", {
          school_id: selectedSchool.id,
          term_id: selectedTerm.id,
          subject_id: subjectId,
        }),
        djangoContext.csrf_token,
        "POST",
        JSON.stringify({})
      );

    const result = await refreshClassesFetchState.fetchData(callback);
    if (result.ok) console.log(result.data);
  }

  return (
    <Layout title="Course Searcher Admin" Navbar={Navbar}>
      <Card className="p-3">
        <Card.Title>Currently available terms and schools</Card.Title>
        <Card.Body>
          <p>{props.schools.length} schools available</p>
          <p>{props.terms_available.length} terms available</p>
          <ListGroup as="ol" variant="flush" numbered className="mb-3 mh-75-vh overflow-auto">
            {props.terms_available.map((term) => (
              <ListGroup.Item key={term.id} as="li">
                {term.full_term_name}
              </ListGroup.Item>
            ))}
          </ListGroup>

          <ButtonWithSpinner
            className="btn btn-primary d-block mb-3"
            isLoadingState={isAnyFetcherLoading}
            hideChildren={false}
            type="button"
            size="sm"
            spinnerVariant="light"
            onClick={handleRefreshTerms}
          >
            Refresh Available Terms and Schools
          </ButtonWithSpinner>
        </Card.Body>
      </Card>

      <Card className="p-3">
        <Card.Title>
          <h3>Refresh Classes</h3>
        </Card.Title>
        <Card.Body>
          <label className="mb-3 form-label">Schools</label>
          <select
            className="form-select"
            onChange={(e) => {
              setSelectedSchool(
                () => props.schools.find((school) => school.id.toString() === e.target.value)!
              );
            }}
          >
            {props.schools.map((school) => (
              <option key={school.id} value={school.id}>
                {school.name}
              </option>
            ))}
          </select>

          <label className="mb-3 form-label">Available Terms:</label>
          <select
            className="form-select mb-3"
            onChange={(e) =>
              setSelectedTerm(
                () => props.terms_available.find((term) => term.id.toString() === e.target.value)!
              )
            }
          >
            {props.terms_available.map((term) => {
              return (
                <option key={term.id} value={term.id}>
                  {term.full_term_name}
                </option>
              );
            })}
          </select>

          {selectedSchool !== undefined && selectedTerm !== undefined && (
            <>
              <ButtonWithSpinner
                type="button"
                className="btn btn-primary d-block mb-3"
                size="sm"
                spinnerVariant="light"
                onClick={handleRefreshSubjectsData}
                isLoadingState={isAnyFetcherLoading}
              >
                Refresh Available Subjects for {selectedSchool.name}
                {selectedSchool.id === 0 ? " schools" : ""}, {selectedTerm.full_term_name}
              </ButtonWithSpinner>
              <ButtonWithSpinner
                type="button"
                className="btn btn-primary d-block mb-3"
                size="sm"
                spinnerVariant="light"
                onClick={handleRefreshClassesData}
                isLoadingState={isAnyFetcherLoading}
              >
                Refresh Class List {selectedSchool.name}, {selectedTerm.full_term_name}
              </ButtonWithSpinner>
            </>
          )}
        </Card.Body>
      </Card>
    </Layout>
  );
}
