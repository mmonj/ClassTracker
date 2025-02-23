import React from "react";

import { Context, interfaces, reverse, templates } from "@reactivated";
import { Card, ListGroup } from "react-bootstrap";

import { fetchByReactivated } from "@client/utils";

import { ButtonWithSpinner } from "@client/components/ButtonWithSpinner";
import { Navbar } from "@client/components/Navbar";
import { useFetch } from "@client/hooks/useFetch";
import { Layout } from "@client/layouts/Layout";

const ALL_SCHOOLS_ID = 0;

export function Template(props: templates.Admin) {
  const [availableSchools, setAvailableSchools] = React.useState([
    { id: ALL_SCHOOLS_ID, name: "All" },
    ...props.schools,
  ]);
  const [availableTerms, setAvailableTerms] = React.useState(props.terms_available);
  const [availableSubjects, setAvailableSubjects] = React.useState<
    interfaces.RespSubjectsUpdate["available_subjects"]
  >([]);

  const [selectedSchool, setSelectedSchool] = React.useState(availableSchools.at(0));
  const [selectedTerm, setSelectedTerm] = React.useState(availableTerms.at(0));
  const [selectedSubject, setSelectedSubject] = React.useState(availableSubjects.at(0));

  const refreshTermsFetchState = useFetch<interfaces.RespSchoolsTermsUpdate>();
  const refreshSubjectsFetchState = useFetch<interfaces.RespSubjectsUpdate>();
  const refreshClassesFetchState = useFetch<interfaces.BasicResponse>();

  const djangoContext = React.useContext(Context);

  const isAnyFetcherLoading =
    refreshTermsFetchState.isLoading ||
    refreshSubjectsFetchState.isLoading ||
    refreshClassesFetchState.isLoading;

  // ====================== Begin functions ======================

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

  async function handleRefreshSemesterData() {
    if (selectedSchool === undefined || selectedTerm === undefined) {
      console.error("No school or term exists");
      return;
    }

    if (selectedSchool.id === ALL_SCHOOLS_ID) {
      const userResp = confirm("Are you sure you want to get semester data for All schools?");
      if (!userResp) return;
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
    if (!result.ok) return;

    setAvailableSubjects(result.data.available_subjects);
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

  function handleSchoolChange(event: React.ChangeEvent<HTMLSelectElement>) {
    setSelectedSchool(
      availableSchools.find((school) => school.id.toString() === event.target.value)
    );
  }

  function handleTermChange(event: React.ChangeEvent<HTMLSelectElement>) {
    setSelectedTerm(availableTerms.find((term) => term.id.toString() === event.target.value));
  }

  // ====================== End functions ======================

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
        <Card.Title>Refresh Classes</Card.Title>
        <Card.Body>
          <div className="mb-3">
            <label className="form-label">School</label>
            <select className="form-select" onChange={handleSchoolChange}>
              {availableSchools.map((school) => (
                <option key={school.id} value={school.id}>
                  {school.name}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-3">
            <label className="form-label">Term:</label>
            <select className="form-select" onChange={handleTermChange}>
              {availableTerms.map((term) => {
                return (
                  <option key={term.id} value={term.id}>
                    {term.full_term_name}
                  </option>
                );
              })}
            </select>
          </div>

          {selectedSchool !== undefined && selectedSchool.id != ALL_SCHOOLS_ID && (
            <div className="mb-3">
              <label className="form-label">Subject</label>
              <select className="form-select">
                {availableSubjects.map((subject) => (
                  <option key={subject.id}>{subject.name}</option>
                ))}
              </select>
            </div>
          )}

          {selectedSchool !== undefined && selectedTerm !== undefined && (
            <>
              <ButtonWithSpinner
                type="button"
                size="sm"
                spinnerVariant="light"
                className="btn btn-primary d-block mb-3"
                onClick={handleRefreshSemesterData}
                isLoadingState={isAnyFetcherLoading}
              >
                Refresh Available Subjects for{" "}
                <b>
                  {selectedSchool.name}
                  {selectedSchool.id === ALL_SCHOOLS_ID ? " schools" : ""},{" "}
                  {selectedTerm.full_term_name}
                </b>
              </ButtonWithSpinner>

              {selectedSchool.id !== ALL_SCHOOLS_ID && (
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
              )}
            </>
          )}
        </Card.Body>
      </Card>
    </Layout>
  );
}
