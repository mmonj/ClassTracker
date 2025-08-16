import React from "react";

import { templates } from "@reactivated";
import { Table } from "react-bootstrap";

interface Props {
  alerts: templates.TrackerClassAlerts["class_alerts"];
  formatDateTime: (dateTime: string) => string;
  getDaysAndTimesString: (
    instructionEntries: templates.TrackerClassAlerts["class_alerts"][0]["course_section"]["instruction_entries"],
  ) => string;
  getInstructorsString: (
    instructionEntries: templates.TrackerClassAlerts["class_alerts"][0]["course_section"]["instruction_entries"],
  ) => string;
}

export function AlertsTable({
  alerts,
  formatDateTime,
  getDaysAndTimesString,
  getInstructorsString,
}: Props) {
  return (
    <div className="table-responsive">
      <Table striped hover>
        <thead>
          <tr>
            <th>Date/Time</th>
            <th>Recipient</th>
            <th>Course</th>
            <th>Section</th>
            <th>Subject</th>
            <th>Term</th>
            <th>Topic</th>
            <th>Days & Times</th>
            <th>Instructors</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert) => (
            <tr key={alert.id}>
              <td>{formatDateTime(alert.datetime_created)}</td>
              <td>{alert.recipient.name}</td>
              <td>
                {alert.course_section.course.code} {alert.course_section.course.level}
              </td>
              <td>{alert.course_section.number}</td>
              <td>{alert.course_section.course.subject.name}</td>
              <td>{alert.course_section.term.full_term_name}</td>
              <td>{alert.course_section.topic}</td>
              <td>{getDaysAndTimesString(alert.course_section.instruction_entries)}</td>
              <td>{getInstructorsString(alert.course_section.instruction_entries)}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}
