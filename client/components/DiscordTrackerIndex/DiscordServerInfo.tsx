import React from "react";

import { templates } from "@reactivated";
import { Badge, Card, Col, Row } from "react-bootstrap";

interface Props {
  server: templates.DiscordTrackerIndex["public_servers"][number];
  className?: string;
}

export function DiscordServerInfo({ server, className }: Props) {
  const hasSubjects = server.subjects.length > 0;
  const hasCourses = server.courses.length > 0;
  const hasInstructors = server.instructors.length > 0;
  const isGeneralServer = server.is_general_server;
  console.log("isGeneralServer:", isGeneralServer);

  if (!hasSubjects && !hasCourses && !hasInstructors && !isGeneralServer) {
    return null;
  }

  return (
    <Card className={className}>
      <Card.Body className="p-3">
        <Card.Title className="h6 text-muted mb-3">Server Information</Card.Title>
        <Row className="g-2">
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
                <small className="text-muted fw-bold">Instructors: </small>
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
