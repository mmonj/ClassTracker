import React, { useContext, useEffect, useState } from "react";

import { Context, interfaces, reverse, templates } from "@reactivated";
import { Alert, Button, Card, Collapse, Container, Form, Row } from "react-bootstrap";
import Select, { SingleValue } from "react-select";

import { faDiscord } from "@fortawesome/free-brands-svg-icons";
import { faChevronDown, faChevronUp, faPlus, faSearch } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import { fetchByReactivated } from "@client/utils";

import {
  AddInviteModal,
  DiscordServerCard,
  LoginBanner,
  ViewInvitesModal,
} from "@client/components/DiscordTrackerServerListings";
import { Navbar } from "@client/components/discord_tracker/Navbar";
import { useFetch } from "@client/hooks/useFetch";
import { Layout } from "@client/layouts/Layout";

interface SubjectOption {
  value: number;
  label: string;
}

interface CourseOption {
  value: number;
  label: string;
}

export function Template(props: templates.DiscordTrackerServerListings) {
  const context = useContext(Context);

  const [selectedServer, setSelectedServer] = useState<(typeof props.public_servers)[0] | null>(
    null,
  );
  const [showInvitesModal, setShowInvitesModal] = useState(false);
  const [showAddInviteModal, setShowAddInviteModal] = useState(false);

  const [publicCollapsed, setPublicCollapsed] = useState(false);
  const [privateCollapsed, setPrivateCollapsed] = useState(false);

  const [selectedSubject, setSelectedSubject] = useState<SubjectOption | null>(
    props.subject_id !== null ? { value: props.subject_id, label: "Loading..." } : null,
  );
  const [selectedCourse, setSelectedCourse] = useState<CourseOption | null>(
    props.course_id !== null ? { value: props.course_id, label: "Loading..." } : null,
  );
  const [subjects, setSubjects] = useState<SubjectOption[]>([]);
  const [courses, setCourses] = useState<CourseOption[]>([]);

  const canUserAddInvites = context.user.discord_user !== null;
  const isAuthenticated = context.user.discord_user !== null;
  const isManager = context.user.discord_user?.role_info.value === "manager";

  const subjectsFetcher = useFetch<interfaces.GetSubjectsResponse>();
  const coursesFetcher = useFetch<interfaces.GetCoursesResponse>();

  useEffect(() => {
    async function fetchSubjects() {
      if (!isAuthenticated) return;

      const result = await subjectsFetcher.fetchData(() =>
        fetchByReactivated(reverse("discord_tracker:get_all_subjects"), context.csrf_token, "GET"),
      );

      if (!result.ok) return;

      const subjectOptions = result.data.subjects.map((subject) => ({
        value: subject.id,
        label: subject.name,
      }));
      setSubjects(subjectOptions);

      // update selected subject label if it was pre-selected
      if (props.subject_id !== null) {
        const foundSubject = subjectOptions.find((subject) => subject.value === props.subject_id);
        if (foundSubject) {
          setSelectedSubject(foundSubject);
        }
      }
    }

    void fetchSubjects();
  }, [isAuthenticated]);

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

  // restore course selection when courses are loaded and course_id prop exists
  useEffect(() => {
    if (courses.length > 0 && props.course_id !== null && !selectedCourse) {
      const foundCourse = courses.find((c: CourseOption) => c.value === props.course_id);
      if (foundCourse) {
        setSelectedCourse(foundCourse);
      }
    }
  }, [courses, props.course_id, selectedCourse]);

  function handleSubjectChange(option: SingleValue<SubjectOption>) {
    setSelectedSubject(option);
    setSelectedCourse(null);
  }

  function handleCourseChange(option: SingleValue<CourseOption>) {
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

      url.searchParams.delete("page");
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
      window.location.href = url.pathname;
    }
  }

  function handleShowInvites(serverId: number) {
    const allServers = [...props.public_servers, ...props.private_servers, ...props.servers];
    const server = allServers.find((s) => s.id === serverId);
    if (server !== undefined) {
      setSelectedServer(server);
      setShowInvitesModal(true);
    }
  }

  function handleCloseModal() {
    setShowInvitesModal(false);
    setSelectedServer(null);
  }

  function handleCloseAddInviteModal() {
    setShowAddInviteModal(false);
  }

  function handleCollapseAll() {
    const shouldCollapse = !publicCollapsed || !privateCollapsed;
    setPublicCollapsed(shouldCollapse);
    setPrivateCollapsed(shouldCollapse);
  }

  function handlePageChange(page: number) {
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      url.searchParams.set("page", page.toString());
      window.location.href = url.toString();
    }
  }

  return (
    <Layout title="Discord Tracker" Navbar={Navbar}>
      <Container className="px-0">
        {context.user.discord_user === null && <LoginBanner />}

        {/* pending invites banner (managers only) */}
        {isManager && props.pending_invites_count > 0 && (
          <Alert variant="warning" className="mb-4">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <strong>{props.pending_invites_count}</strong> pending invite submission(s) awaiting
                approval
              </div>
              <Button
                variant="outline-secondary"
                size="sm"
                href={reverse("discord_tracker:unapproved_invites")}
              >
                Review Invites
              </Button>
            </div>
          </Alert>
        )}

        <div className="text-center mb-5">
          <div className="d-flex align-items-center justify-content-center mb-3">
            <FontAwesomeIcon icon={faDiscord} size="3x" className="text-primary me-3" />
            <h1 className="h2 mb-0">Discord Servers</h1>
          </div>
          <p className="text-muted lead">Discover and join Discord servers for your classes</p>

          {/* search filters */}
          {isAuthenticated && (
            <Card className="mb-4 p-2">
              <Card.Header>
                <div className="d-flex align-items-center">
                  <FontAwesomeIcon icon={faSearch} className="me-2" />
                  <h5 className="mb-0">Search Servers</h5>
                </div>
              </Card.Header>
              <Card.Body>
                <Form onSubmit={handleSearchSubmit}>
                  <Row className="g-3">
                    <div className="col-md-4">
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
                    </div>
                    <div className="col-md-4">
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
                    </div>
                    <div className="col-md-4 d-flex align-items-end gap-2">
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
                      {/* clear search filters */}
                      <Button type="button" variant="outline-secondary" onClick={clearSearch}>
                        Clear
                      </Button>
                    </div>
                  </Row>
                </Form>
              </Card.Body>
            </Card>
          )}

          {/* 'add invite' button */}
          {canUserAddInvites && (
            <div className="mt-3">
              <Button
                variant="success"
                onClick={() => setShowAddInviteModal((prev) => !prev)}
                className="d-flex align-items-center mx-auto"
              >
                <FontAwesomeIcon icon={faPlus} className="me-2" />
                Add Discord Invite
              </Button>
            </div>
          )}
        </div>

        {/* search results */}
        {props.is_search_active && (
          <section className="mb-5">
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h2 className="h3 mb-0">Search Results</h2>
            </div>

            {props.servers.length > 0 ? (
              <Row>
                {props.servers.map((server) => (
                  <DiscordServerCard
                    key={server.id}
                    server={server}
                    onShowInvites={handleShowInvites}
                  />
                ))}
              </Row>
            ) : (
              <Alert variant="info">No servers found matching your search criteria.</Alert>
            )}

            {/* pagination for search results */}
            {props.pagination && props.pagination.total_pages > 1 && (
              <nav className="mt-4">
                <ul className="pagination justify-content-center">
                  {props.pagination.has_previous && (
                    <li className="page-item">
                      <button
                        className="page-link"
                        onClick={() => handlePageChange(props.pagination!.previous_page_number)}
                      >
                        Previous
                      </button>
                    </li>
                  )}

                  {Array.from({ length: props.pagination.total_pages || 0 }, (_, i) => i + 1).map(
                    (pageNum) => (
                      <li
                        key={pageNum}
                        className={classNames("page-item", {
                          active: pageNum === props.pagination?.current_page,
                        })}
                      >
                        <button className="page-link" onClick={() => handlePageChange(pageNum)}>
                          {pageNum}
                        </button>
                      </li>
                    ),
                  )}

                  {props.pagination.has_next && (
                    <li className="page-item">
                      <button
                        className="page-link"
                        onClick={() => handlePageChange(props.pagination!.next_page_number)}
                      >
                        Next
                      </button>
                    </li>
                  )}
                </ul>
              </nav>
            )}
          </section>
        )}

        {/* Normal view when no filters are set */}
        {!props.is_search_active && (
          <>
            {/* 'toggle all' button (for collapsible sections) */}
            {(props.public_servers.length > 0 || props.private_servers.length > 0) && (
              <div className="text-center mb-4">
                <Button
                  variant="outline-secondary"
                  size="sm"
                  onClick={handleCollapseAll}
                  className="d-flex align-items-center mx-auto"
                >
                  <FontAwesomeIcon
                    icon={publicCollapsed && privateCollapsed ? faChevronDown : faChevronUp}
                    className="me-2"
                  />
                  {publicCollapsed && privateCollapsed ? "Expand All" : "Collapse All"}
                </Button>
              </div>
            )}

            {/* public servers */}
            {props.public_servers.length > 0 && (
              <section className="mb-5">
                <div
                  className={classNames(
                    "d-flex justify-content-between align-items-center mb-3 p-3 rounded cursor-pointer user-select-none border-bottom",
                    {
                      "bg-light": publicCollapsed,
                    },
                  )}
                  onClick={() => setPublicCollapsed(!publicCollapsed)}
                  style={{ cursor: "pointer" }}
                >
                  <h2 className="h3 mb-0">Public Servers</h2>
                  <FontAwesomeIcon icon={publicCollapsed ? faChevronDown : faChevronUp} />
                </div>
                <Collapse in={!publicCollapsed}>
                  <div>
                    <Row>
                      {props.public_servers.map((server) => (
                        <DiscordServerCard
                          key={server.id}
                          server={server}
                          onShowInvites={handleShowInvites}
                        />
                      ))}
                    </Row>
                  </div>
                </Collapse>
              </section>
            )}

            {/* private servers section */}
            {props.private_servers.length > 0 && (
              <section className="mb-5">
                <div
                  className={classNames(
                    "d-flex justify-content-between align-items-center mb-3 p-3 rounded cursor-pointer user-select-none border-bottom",
                    {
                      "bg-light": privateCollapsed,
                    },
                  )}
                  onClick={() => setPrivateCollapsed(!privateCollapsed)}
                  style={{ cursor: "pointer" }}
                >
                  <h2 className="h3 mb-0">Private Servers</h2>
                  <FontAwesomeIcon icon={privateCollapsed ? faChevronDown : faChevronUp} />
                </div>
                <Collapse in={!privateCollapsed}>
                  <div>
                    <Alert variant="info" className="mb-3">
                      <b>Note:</b> These servers' invites are only visible to authenticated users
                    </Alert>
                    <Row>
                      {props.private_servers.map((server) => (
                        <DiscordServerCard
                          key={server.id}
                          server={server}
                          onShowInvites={handleShowInvites}
                        />
                      ))}
                    </Row>
                  </div>
                </Collapse>
              </section>
            )}
          </>
        )}

        {/* 'no servers' msg */}
        {!props.is_search_active &&
          props.public_servers.length === 0 &&
          props.private_servers.length === 0 && (
            <div className="text-center py-5">
              <Card className="border-0">
                <Card.Body>
                  <FontAwesomeIcon icon={faDiscord} size="4x" className="text-muted mb-3" />
                  <h3 className="text-muted">No Discord Servers Available</h3>
                  <p className="text-muted">No Discord servers have been added yet</p>
                </Card.Body>
              </Card>
            </div>
          )}

        <ViewInvitesModal
          show={showInvitesModal}
          onHide={handleCloseModal}
          server={selectedServer}
        />

        <AddInviteModal show={showAddInviteModal} onHide={handleCloseAddInviteModal} />
      </Container>
    </Layout>
  );
}
