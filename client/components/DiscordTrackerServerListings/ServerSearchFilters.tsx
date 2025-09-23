import React, { useContext, useEffect, useState } from "react";

import { Button, Card, Col, Form, Row } from "react-bootstrap";
import Select, { SingleValue } from "react-select";

import { Context, interfaces, reverse } from "@reactivated";

import { faSearch } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { useFetch } from "@client/hooks/useFetch";
import { fetchByReactivated } from "@client/utils";

interface SelectOption {
  value: number;
  label: string;
}

interface ServerSearchFiltersProps {
  subjectId?: number | null;
  courseId?: number | null;
}

export function ServerSearchFilters({ subjectId, courseId }: ServerSearchFiltersProps) {
  const context = useContext(Context);

  const [selectedSubject, setSelectedSubject] = useState<SelectOption | null>(
    subjectId !== null && subjectId !== undefined
      ? { value: subjectId, label: "Loading..." }
      : null,
  );
  const [selectedCourse, setSelectedCourse] = useState<SelectOption | null>(
    courseId !== null && courseId !== undefined ? { value: courseId, label: "Loading..." } : null,
  );
  const [subjects, setSubjects] = useState<SelectOption[]>([]);
  const [courses, setCourses] = useState<SelectOption[]>([]);

  const subjectsFetcher = useFetch<interfaces.GetSubjectsResponse>();
  const coursesFetcher = useFetch<interfaces.GetCoursesResponse>();

  // fetch subjects when component mounts
  useEffect(() => {
    async function fetchSubjects() {
      const result = await subjectsFetcher.fetchData(() =>
        fetchByReactivated(reverse("discord_tracker:get_all_subjects"), context.csrf_token, "GET"),
      );

      if (!result.ok) return;

      const subjectOptions = result.data.subjects.map((subject) => ({
        value: subject.id,
        label: subject.name,
      }));
      setSubjects(subjectOptions);

      // Update selected subject label if it was pre-selected
      if (subjectId !== null && subjectId !== undefined) {
        const foundSubject = subjectOptions.find((subject) => subject.value === subjectId);
        if (foundSubject) {
          setSelectedSubject(foundSubject);
        }
      }
    }

    void fetchSubjects();
  }, []);

  // fetch courses when subject changes
  useEffect(() => {
    async function fetchCourses() {
      if (!selectedSubject) {
        setCourses([]);
        setSelectedCourse(null);
        return;
      }

      const result = await coursesFetcher.fetchData(() =>
        fetchByReactivated(
          reverse("discord_tracker:get_all_courses", { subject_id: selectedSubject.value }),
          context.csrf_token,
          "GET",
        ),
      );

      if (!result.ok) return;

      const courseOptions = result.data.courses.map((course) => ({
        value: course.id,
        label: `${course.code} ${course.level} - ${course.title}`,
      }));
      setCourses(courseOptions);
    }

    void fetchCourses();
  }, [selectedSubject]);

  // restore course selection when courses are loaded and courseId prop exists
  useEffect(() => {
    if (
      courses.length > 0 &&
      courseId !== null &&
      courseId !== undefined &&
      selectedCourse?.label === "Loading..."
    ) {
      const foundCourse = courses.find((c: SelectOption) => c.value === courseId);
      if (foundCourse) {
        setSelectedCourse(foundCourse);
      }
    }
  }, [courses, courseId, selectedCourse]);

  function handleSubjectChange(option: SingleValue<SelectOption>) {
    setSelectedSubject(option);
    setSelectedCourse(null);
  }

  function handleCourseChange(option: SingleValue<SelectOption>) {
    setSelectedCourse(option);
  }

  function executeSearch() {
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);

      if (selectedSubject) {
        url.searchParams.set("subject_id", selectedSubject.value.toString());
      } else {
        url.searchParams.delete("subject_id");
      }

      if (selectedCourse) {
        url.searchParams.set("course_id", selectedCourse.value.toString());
      } else {
        url.searchParams.delete("course_id");
      }

      url.searchParams.set("page", "1");
      window.location.href = url.toString();
    }
  }

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    executeSearch();
  }

  function clearSearch() {
    setSelectedSubject(null);
    setSelectedCourse(null);

    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      url.searchParams.delete("subject_id");
      url.searchParams.delete("course_id");
      // keep 'page' url query param
      window.location.href = url.toString();
    }
  }

  return (
    <Card className="mb-4 py-2 px-1">
      <Card.Header>
        <div className="d-flex align-items-center">
          <FontAwesomeIcon icon={faSearch} className="me-2" />
          <h5 className="mb-0">Search Servers</h5>
        </div>
      </Card.Header>
      <Card.Body>
        <Form onSubmit={handleSearchSubmit}>
          <Row className="g-3">
            <Col md={4}>
              <Form.Label>Subject</Form.Label>
              <Select
                value={selectedSubject}
                onChange={handleSubjectChange}
                options={subjects}
                isClearable
                placeholder="Select a subject..."
                classNamePrefix="react-select"
                isLoading={subjectsFetcher.isLoading}
                isDisabled={subjectsFetcher.isLoading}
              />
            </Col>
            <Col md={4}>
              <Form.Label>Course</Form.Label>
              <Select
                value={selectedCourse}
                onChange={handleCourseChange}
                options={courses}
                isClearable
                placeholder="Select a course..."
                isDisabled={selectedSubject === null || coursesFetcher.isLoading}
                classNamePrefix="react-select"
                isLoading={coursesFetcher.isLoading}
              />
            </Col>
            <Col md={4} className="d-flex align-items-end gap-2">
              <Button
                type="submit"
                variant="primary"
                className="flex-grow-1"
                disabled={
                  (!selectedSubject && !selectedCourse) ||
                  subjectsFetcher.isLoading ||
                  coursesFetcher.isLoading
                }
              >
                <FontAwesomeIcon icon={faSearch} className="me-2" />
                Search
              </Button>
              <Button type="button" variant="outline-secondary" onClick={clearSearch}>
                Clear
              </Button>
            </Col>
          </Row>
        </Form>
      </Card.Body>
    </Card>
  );
}
