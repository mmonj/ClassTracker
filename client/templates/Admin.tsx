import React from "react";

import { Context, interfaces, reverse, templates } from "@reactivated";
import { Card, ListGroup } from "react-bootstrap";

import { faSync } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

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
  const getSubjectsFetchState = useFetch<interfaces.RespGetSubjects>();
  const refreshClassesFetchState = useFetch<interfaces.BasicResponse>();

  const djangoContext = React.useContext(Context);

  const isAnyFetcherLoading =
    refreshTermsFetchState.isLoading ||
    refreshSubjectsFetchState.isLoading ||
    refreshClassesFetchState.isLoading;

  // =======================================================================================================================
  // =================================================== Begin functions ===================================================
  // =======================================================================================================================

  async function handleRefreshTerms() {
    const fetchCallback = () =>
      fetchByReactivated(
        reverse("class_tracker:refresh_available_terms"),
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
        reverse("class_tracker:refresh_semester_data", {
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

  async function handleRefreshClassesData(schoolId: number, termId: number, subjectId: number) {
    const callback = () =>
      fetchByReactivated(
        reverse("class_tracker:refresh_class_data", {
          school_id: schoolId,
          term_id: termId,
          subject_id: subjectId,
        }),
        djangoContext.csrf_token,
        "POST"
      );

    const result = await refreshClassesFetchState.fetchData(callback);
    if (!result.ok) return;
    alert("Success!");
  }

  async function getSubjects() {
    if (selectedSchool === undefined || selectedTerm === undefined) return;
    if (selectedSchool.id == ALL_SCHOOLS_ID) return;

    const callback = () =>
      fetchByReactivated(
        reverse("class_tracker:get_subjects", {
          school_id: selectedSchool.id,
          term_id: selectedTerm.id,
        }),
        djangoContext.csrf_token,
        "GET"
      );
    const result = await getSubjectsFetchState.fetchData(callback);
    if (result.ok) {
      setAvailableSubjects(result.data.subjects);
    }
  }

  function handleSchoolChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const school = availableSchools.find((school) => school.id.toString() === event.target.value);
    setSelectedSchool(school);
  }

  function handleTermChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const term = availableTerms.find((term) => term.id.toString() === event.target.value);
    setSelectedTerm(term);
  }

  function handleSubjectChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const subject = availableSubjects.find(
      (subject) => subject.id.toString() === event.target.value
    );
    setSelectedSubject(subject);
  }

  // =======================================================================================================================
  // ==================================================== End functions ====================================================
  // =======================================================================================================================

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
            variant="light"
            hideChildren={false}
            className="btn btn-primary d-block mb-3"
            onClick={handleRefreshTerms}
            isLoadingState={isAnyFetcherLoading}
          >
            Parse for new Terms and Schools
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
              <div className="d-flex">
                <select className="form-select" onChange={handleSubjectChange}>
                  {availableSubjects.map((subject) => (
                    <option key={subject.id} value={subject.id}>
                      {subject.name}
                    </option>
                  ))}
                </select>
                <ButtonWithSpinner
                  type="button"
                  size="sm"
                  hideChildren={true}
                  className="btn btn-primary ms-2"
                  disabled={selectedSchool.id === ALL_SCHOOLS_ID}
                  isLoadingState={getSubjectsFetchState.isLoading}
                  onClick={getSubjects}
                >
                  <FontAwesomeIcon icon={faSync} size="1x" />
                </ButtonWithSpinner>
              </div>
            </div>
          )}

          {selectedSchool !== undefined && selectedTerm !== undefined && (
            <>
              <ButtonWithSpinner
                type="button"
                size="sm"
                variant="light"
                className="btn btn-primary d-block mb-3"
                onClick={handleRefreshSemesterData}
                isLoadingState={isAnyFetcherLoading}
              >
                Parse for new Subjects for{" "}
                <b>
                  {selectedSchool.name}
                  {selectedSchool.id === ALL_SCHOOLS_ID ? " schools" : ""},{" "}
                  {selectedTerm.full_term_name}
                </b>
              </ButtonWithSpinner>

              {selectedSchool.id !== ALL_SCHOOLS_ID && selectedSubject !== undefined && (
                <ButtonWithSpinner
                  type="button"
                  size="sm"
                  variant="light"
                  className="btn btn-primary d-block mb-3"
                  onClick={() =>
                    handleRefreshClassesData(selectedSchool.id, selectedTerm.id, selectedSubject.id)
                  }
                  isLoadingState={isAnyFetcherLoading}
                >
                  Parse for new Course sections for{" "}
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
