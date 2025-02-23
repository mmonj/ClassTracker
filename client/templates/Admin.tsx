import React from "react";

import { Context, interfaces, reverse, templates } from "@reactivated";
import { Card, ListGroup } from "react-bootstrap";

import { fetchByReactivated } from "@client/utils";

import { ButtonWithSpinner } from "@client/components/ButtonWithSpinner";
import { Navbar } from "@client/components/Navbar";
import { useFetch } from "@client/hooks/useFetch";
import { Layout } from "@client/layouts/Layout";

export function Template(props: templates.Admin) {
  const [availableSchools, setAvailableSchools] = React.useState([
    { id: 0, name: "All" },
    ...props.schools,
  ]);
  const [availableTerms, setAvailableTerms] = React.useState(props.terms_available);

  const [selectedSchool, setSelectedSchool] = React.useState(availableSchools.at(0));
  const [selectedTerm, setSelectedTerm] = React.useState(availableTerms.at(0));

  const refreshTermsFetchState = useFetch<interfaces.RespSchoolsTermsUpdate>();
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
    if (!fetchResult.ok) {
      console.log(fetchResult.errors);
      return;
    }

    setAvailableSchools(fetchResult.data.available_schools);
    setAvailableTerms(fetchResult.data.available_terms);
    alert(`${fetchResult.data.new_terms_count} new terms added`);
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
          {/* to account for the 'All' option */}
          <p>{availableSchools.length - 1} schools available</p>
          <p>{availableTerms.length} terms available</p>
          <ListGroup as="ol" variant="flush" numbered className="mb-3 mh-75-vh overflow-auto">
            {availableTerms.map((term) => (
              <ListGroup.Item key={term.id} as="li">
                {term.full_term_name}
              </ListGroup.Item>
            ))}
          </ListGroup>

          <ButtonWithSpinner
            type="button"
            size="sm"
            spinnerVariant="light"
            hideChildren={false}
            className="btn btn-primary d-block mb-3"
            onClick={handleRefreshTerms}
            isLoadingState={isAnyFetcherLoading}
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
                () => availableSchools.find((school) => school.id.toString() === e.target.value)!
              );
            }}
          >
            {availableSchools.map((school) => (
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
                () => availableTerms.find((term) => term.id.toString() === e.target.value)!
              )
            }
          >
            {availableTerms.map((term) => {
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
                size="sm"
                spinnerVariant="light"
                className="btn btn-primary d-block mb-3"
                onClick={handleRefreshSubjectsData}
                isLoadingState={isAnyFetcherLoading}
              >
                Refresh Available Subjects for{" "}
                <b>
                  {selectedSchool.name}
                  {selectedSchool.id === 0 ? " schools" : ""}, {selectedTerm.full_term_name}
                </b>
              </ButtonWithSpinner>
              <ButtonWithSpinner
                type="button"
                size="sm"
                spinnerVariant="light"
                className="btn btn-primary d-block mb-3"
                onClick={handleRefreshClassesData}
                isLoadingState={isAnyFetcherLoading}
              >
                Refresh Class List for{" "}
                <b>
                  {selectedSchool.name}, {selectedTerm.full_term_name}
                </b>
              </ButtonWithSpinner>
            </>
          )}
        </Card.Body>
      </Card>
    </Layout>
  );
}
