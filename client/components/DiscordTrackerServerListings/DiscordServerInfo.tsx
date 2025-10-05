import React from "react";

import { Badge, Card, Col, Row } from "react-bootstrap";

import { templates } from "@reactivated";

import { formatDateTypical } from "@client/utils";

interface Props {
  server: templates.DiscordTrackerExploreAll["servers"][number];
  truncate_description?: boolean;
  className?: string;
}

export function DiscordServerInfo({ server, className, truncate_description = false }: Props) {
  const hasSubjects = server.subjects.length > 0;
  const hasCourses = server.courses.length > 0;
  const hasInstructors = server.instructors.length > 0;
  const isGeneralServer = server.is_general_server;
  const hasDescription = server.description.trim().length > 0;
  const hasEstablishedDate = server.datetime_established !== null;

  if (
    !hasSubjects &&
    !hasCourses &&
    !hasInstructors &&
    !isGeneralServer &&
    !hasDescription &&
    !hasEstablishedDate
  ) {
    return null;
  }

  function getFormattedDescription(description: string) {
    const maxLength = 100;
    description = description.trim();

    if (truncate_description && description.length > maxLength) {
      return description.slice(0, maxLength) + "...";
    }
    return description;
  }

  return (
    <Card className={className}>
      <Card.Body className="p-3">
        <Card.Title className="mb-3">
          <span className="h6 text-bold border-bottom">Server Information</span>
        </Card.Title>
        <Row className="g-2">
          {hasDescription && (
            <Col xs={12} className="mt-0">
              <div className="mb-1">
                <p className="mb-0 small text-break">
                  {getFormattedDescription(server.description)}
                </p>
              </div>
            </Col>
          )}

          {hasEstablishedDate && (
            <Col xs={12} className="mt-0">
              <div className="mb-1">
                <small className="text-muted fw-bold">Established: </small>
                <Badge bg="info" className="text-dark">
                  {formatDateTypical(server.datetime_established, { showTime: false })}
                </Badge>
              </div>
            </Col>
          )}

          {hasSubjects && (
            <Col xs={12} className="mt-0">
              <div className="mb-1">
                <small className="text-muted fw-bold">Subject(s): </small>
                <div className="mt-1">
                  {server.subjects.map((subject) => (
                    <Badge key={subject.id} bg="secondary" className="me-1 mb-1 text-dark">
                      {subject.name}
                    </Badge>
                  ))}
                </div>
              </div>
            </Col>
          )}

          {isGeneralServer && (
            <Col xs={12} className="mt-0">
              <div className="mb-2 mb-1">
                <small className="text-muted fw-bold">Type: </small>
                <Badge bg="info" className="text-dark">
                  General Server
                </Badge>
              </div>
            </Col>
          )}

          {hasCourses && (
            <Col xs={12} className="mt-0">
              <div className="mb-1">
                <small className="text-muted fw-bold">Course(s): </small>
                <div className="mt-1">
                  {server.courses.map((course) => (
                    <Badge key={course.id} bg="primary" className="me-1 mb-1 text-dark">
                      {course.code} {course.level} - {course.title}
                    </Badge>
                  ))}
                </div>
              </div>
            </Col>
          )}

          {hasInstructors && (
            <Col xs={12} className="mt-0">
              <div className="mb-1">
                <small className="text-muted fw-bold">Instructor(s): </small>
                <div className="mt-1">
                  {server.instructors.map((instructor) => (
                    <Badge key={instructor.id} bg="warning" className="me-1 mb-1">
                      {instructor.name}
                    </Badge>
                  ))}
                </div>
              </div>
            </Col>
          )}
        </Row>
      </Card.Body>
    </Card>
  );
}
