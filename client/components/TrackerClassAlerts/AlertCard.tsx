import React from "react";

import { templates } from "@reactivated";
import { Card } from "react-bootstrap";

import { faBell, faClock, faGraduationCap, faUser } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

interface Props {
  alert: templates.TrackerClassAlerts["class_alerts"][0];
  formatDateTime: (dateTime: string) => string;
  getDaysAndTimesString: (
    instructionEntries: templates.TrackerClassAlerts["class_alerts"][0]["course_section"]["instruction_entries"],
  ) => string;
  getInstructorsString: (
    instructionEntries: templates.TrackerClassAlerts["class_alerts"][0]["course_section"]["instruction_entries"],
  ) => string;
}

export function AlertCard({
  alert,
  formatDateTime,
  getDaysAndTimesString,
  getInstructorsString,
}: Props) {
  return (
    <Card className="mb-3">
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start mb-2">
          <div className="d-flex align-items-center gap-2">
            <FontAwesomeIcon icon={faBell} className="text-primary" />
            <h5 className="mb-0">
              {alert.course_section.course.code} {alert.course_section.course.level}
              <span className="text-muted ms-2">Section {alert.course_section.number}</span>
            </h5>
          </div>
          <small className="text-muted">
            <FontAwesomeIcon icon={faClock} className="me-1" />
            {formatDateTime(alert.datetime_created)}
          </small>
        </div>

        <div className="row">
          <div className="col-md-6">
            <div className="mb-2">
              <strong>
                <FontAwesomeIcon icon={faUser} className="me-1 text-muted" />
                Recipient:
              </strong>
              <span className="ms-2">{alert.recipient.name}</span>
            </div>

            <div className="mb-2">
              <strong>Subject:</strong>
              <span className="ms-2">{alert.course_section.course.subject.name}</span>
            </div>

            <div className="mb-2">
              <strong>Term:</strong>
              <span className="ms-2">{alert.course_section.term.full_term_name}</span>
            </div>
          </div>

          <div className="col-md-6">
            {alert.course_section.topic && (
              <div className="mb-2">
                <strong>Topic:</strong>
                <span className="ms-2">{alert.course_section.topic}</span>
              </div>
            )}

            <div className="mb-2">
              <strong>
                <FontAwesomeIcon icon={faClock} className="me-1 text-muted" />
                Schedule:
              </strong>
              <span className="ms-2">
                {getDaysAndTimesString(alert.course_section.instruction_entries)}
              </span>
            </div>

            <div className="mb-2">
              <strong>
                <FontAwesomeIcon icon={faGraduationCap} className="me-1 text-muted" />
                Instructors:
              </strong>
              <span className="ms-2">
                {getInstructorsString(alert.course_section.instruction_entries)}
              </span>
            </div>
          </div>
        </div>
      </Card.Body>
    </Card>
  );
}
