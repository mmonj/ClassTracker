import React from "react";

import { templates } from "@reactivated";
import { ListGroup } from "react-bootstrap";

import { AlertListItem } from "./AlertListItem";

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

export function AlertsList({
  alerts,
  formatDateTime,
  getDaysAndTimesString,
  getInstructorsString,
}: Props) {
  return (
    <ListGroup variant="flush">
      {alerts.map((alert) => (
        <AlertListItem
          key={alert.id}
          alert={alert}
          formatDateTime={formatDateTime}
          getDaysAndTimesString={getDaysAndTimesString}
          getInstructorsString={getInstructorsString}
        />
      ))}
    </ListGroup>
  );
}
