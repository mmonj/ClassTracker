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
const ALL_SUBJECTS_ID = 0;

const ALL_SCHOOLS_OPTION = { id: ALL_SCHOOLS_ID, name: "All Schools" };
const ALL_SUBJECTS_OPTION = { id: ALL_SUBJECTS_ID, name: "All Subjects" };

export function Template(props: templates.TrackerManageCourselist) {
  const [availableSchools, setAvailableSchools] = React.useState([
    ALL_SCHOOLS_OPTION,
    ...props.schools,
  ]);
  const [availableTerms, setAvailableTerms] = React.useState(props.terms_available);
  const [availableSubjects, _setAvailableSubjects] = React.useState<
    interfaces.RespSubjectsUpdate["available_subjects"]
  >([ALL_SUBJECTS_OPTION]);
  const [availableCourses, setAvailableCourses] = React.useState<
    interfaces.RespRefreshCourseSections["courses"] | undefined
  >(undefined);

  const [selectedSchool, setSelectedSchool] = React.useState(availableSchools.at(0));
  const [selectedTerm, setSelectedTerm] = React.useState(availableTerms.at(0));
  const [selectedSubject, setSelectedSubject] = React.useState(availableSubjects.at(0));

  const refreshTermsFetcher = useFetch<interfaces.RespSchoolsTermsUpdate>();
  const refreshSubjectsFetcher = useFetch<interfaces.RespSubjectsUpdate>();
  const getSubjectsFetcher = useFetch<interfaces.RespGetSubjects>();
  const refreshClassesFetcher = useFetch<interfaces.RespRefreshCourseSections>();

  const djangoContext = React.useContext(Context);

  // Create useCallback to make usre that when setting available subjects, we also add the ALL_SUBJECTS_OPTION as first element
  const setAvailableSubjects = React.useCallback(
    (subjects: interfaces.RespSubjectsUpdate["available_subjects"]) => {
      _setAvailableSubjects([ALL_SUBJECTS_OPTION, ...subjects]);
      setSelectedSubject(ALL_SUBJECTS_OPTION);
    },
    [],
  );

  // =======================================================================================================================
  // =================================================== Begin functions ===================================================
  // =======================================================================================================================

  async function handleRefreshSchoolsAndTerms() {
    const fetchCallback = () =>
      fetchByReactivated(
        reverse("class_tracker:refresh_available_terms"),
        djangoContext.csrf_token,
        "POST",
      );

    const fetchResult = await refreshTermsFetcher.fetchData(fetchCallback);
    if (!fetchResult.ok) {
      console.log(fetchResult.errors);
      return;
    }

    setAvailableSchools(fetchResult.data.available_schools);
    setAvailableTerms(fetchResult.data.available_terms);
    setSelectedSchool(fetchResult.data.available_schools.at(0));
    setSelectedTerm(fetchResult.data.available_terms.at(0));

    alert(`${fetchResult.data.new_terms_count} new terms added`);
  }

  async function handleRefreshSchoolTermData() {
    if (selectedSchool === undefined || selectedTerm === undefined) {
      console.error("No school or term exists");
      return;
    }

    if (selectedSchool.id === ALL_SCHOOLS_ID) {
      const userResp = confirm("Are you sure you want to get semester data for All schools?");
      if (!userResp) return;
    }

    console.log(
      `Refreshing subjects for school: ${selectedSchool.name}, term: ${selectedTerm.full_term_name}`,
    );

    const callback = () =>
      fetchByReactivated(
        reverse("class_tracker:refresh_semester_data", {
          school_id: selectedSchool.id,
          term_id: selectedTerm.id,
        }),
        djangoContext.csrf_token,
        "POST",
      );

    const result = await refreshSubjectsFetcher.fetchData(callback);
    if (!result.ok) return;

    setAvailableSubjects(result.data.available_subjects);
  }

  async function handleRefreshClassesData(schoolId: number, termId: number, subjectId: number) {
    console.log(
      `Refreshing classes for school: ${selectedSchool?.name}, term: ${selectedTerm?.name}, subject: ${selectedSubject?.name}`,
    );

    const callback = () =>
      fetchByReactivated(
        reverse("class_tracker:refresh_class_data", {
          school_id: schoolId,
          term_id: termId,
          subject_id: subjectId,
        }),
        djangoContext.csrf_token,
        "POST",
      );

    const result = await refreshClassesFetcher.fetchData(callback);
    if (!result.ok) return;
    setAvailableCourses(result.data.courses);
  }

  async function getSubjects(schoolId: number | undefined, termId: number | undefined) {
    if (schoolId === undefined || termId === undefined) return;
    if (schoolId == ALL_SCHOOLS_ID) return;

    const selectedSchool = availableSchools.find((school) => school.id === schoolId);
    if (selectedSchool === undefined) {
      console.error("Selected school not found in available schools");
      return;
    }

    const selectedTerm = availableTerms.find((term) => term.id === termId);
    if (selectedTerm === undefined) {
      console.error("Selected term not found in available terms");
      return;
    }

    console.log("Fetching subjects for", selectedSchool.name, selectedTerm.full_term_name);

    const callback = () =>
      fetchByReactivated(
        reverse("class_tracker:get_subjects", {
          school_id: selectedSchool.id,
          term_id: selectedTerm.id,
        }),
        djangoContext.csrf_token,
        "GET",
      );
    const result = await getSubjectsFetcher.fetchData(callback);
    if (result.ok) {
      setAvailableSubjects(result.data.subjects);
    }
  }

  function handleSchoolChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const school = availableSchools.find(
      (school) => school.id === Number.parseInt(event.target.value),
    );
    setSelectedSchool(school);

    void getSubjects(school?.id, selectedTerm?.id);
  }

  function handleTermChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const term = availableTerms.find((term) => term.id === Number.parseInt(event.target.value));
    setSelectedTerm(term);

    if (
      term === undefined ||
      selectedSchool === undefined ||
      selectedSchool.id === ALL_SCHOOLS_ID
    ) {
      return;
    }

    void getSubjects(selectedSchool.id, term.id);
  }

  function handleSubjectChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const subject = availableSubjects.find(
      (subject) => subject.id.toString() === event.target.value,
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
            onClick={handleRefreshSchoolsAndTerms}
            isLoadingState={refreshTermsFetcher.isLoading}
          >
            Refresh available Terms and Schools
          </ButtonWithSpinner>
        </Card.Body>
      </Card>

      <Card className="p-3">
        <Card.Title>Refresh Classes</Card.Title>
        <Card.Body>
          <div className="mb-3">
            <label className="form-label">School:</label>
            <select
              className="form-select"
              value={selectedSchool?.id}
              onChange={handleSchoolChange}
              disabled={getSubjectsFetcher.isLoading}
            >
              {availableSchools.map((school) => (
                <option key={school.id} value={school.id}>
                  {school.name}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-3">
            <label className="form-label">Term:</label>
            <select
              className="form-select"
              value={selectedTerm?.id}
              onChange={handleTermChange}
              disabled={getSubjectsFetcher.isLoading}
            >
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
              <label className="form-label">Subject:</label>
              <div className="d-flex">
                <select
                  className="form-select"
                  value={selectedSubject?.id}
                  onChange={handleSubjectChange}
                  disabled={getSubjectsFetcher.isLoading}
                >
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
                  onClick={handleRefreshSchoolTermData}
                  isLoadingState={refreshSubjectsFetcher.isLoading}
                  title={"Refresh available Subjects"}
                >
                  <FontAwesomeIcon icon={faSync} size="1x" />
                </ButtonWithSpinner>
              </div>
            </div>
          )}

          {selectedSchool !== undefined && selectedTerm !== undefined && (
            <>
              {selectedSchool.id !== ALL_SCHOOLS_ID && selectedSubject !== undefined && (
                <ButtonWithSpinner
                  type="button"
                  size="sm"
                  variant="light"
                  className="btn btn-primary d-block mb-3"
                  onClick={() =>
                    handleRefreshClassesData(selectedSchool.id, selectedTerm.id, selectedSubject.id)
                  }
                  isLoadingState={refreshClassesFetcher.isLoading}
                >
                  Refresh available Course sections for{" "}
                  <b>
                    {selectedSchool.name}, {selectedTerm.full_term_name}
                  </b>
                </ButtonWithSpinner>
              )}
            </>
          )}
        </Card.Body>
      </Card>

      {availableCourses !== undefined && !refreshClassesFetcher.isLoading && (
        <Card className="p-3">
          <Card.Title>Available Courses</Card.Title>
          <Card.Body>
            <ListGroup as="ol" variant="flush" numbered className="mh-75-vh overflow-auto">
              {availableCourses.length > 0 &&
                availableCourses.map((course) => (
                  <ListGroup.Item key={course.id} as="li">
                    {course.code} - {course.level} - Sections:{" "}
                    {course.sections.map((section) => section.number).join(", ")}
                  </ListGroup.Item>
                ))}
            </ListGroup>

            {availableCourses.length === 0 && (
              <p className="text-muted">
                No courses available for the {selectedSchool?.name} and{" "}
                {selectedTerm?.full_term_name}
              </p>
            )}
          </Card.Body>
        </Card>
      )}
    </Layout>
  );
}
