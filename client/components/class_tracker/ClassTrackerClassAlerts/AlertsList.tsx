import React from "react";

import { ListGroup } from "react-bootstrap";

import { templates } from "@reactivated";

import { AlertListItem } from "./AlertListItem";

interface Props {
  alerts: templates.ClassTrackerClassAlerts["class_alerts"];
  getDaysAndTimesString: (
    instructionEntries: templates.ClassTrackerClassAlerts["class_alerts"][0]["course_section"]["instruction_entries"],
  ) => string;
  getInstructorsString: (
    instructionEntries: templates.ClassTrackerClassAlerts["class_alerts"][0]["course_section"]["instruction_entries"],
  ) => string;
}

export function AlertsList({ alerts, getDaysAndTimesString, getInstructorsString }: Props) {
  return (
    <ListGroup variant="flush">
      {alerts.map((alert) => (
        <AlertListItem
          key={alert.id}
          alert={alert}
          getDaysAndTimesString={getDaysAndTimesString}
          getInstructorsString={getInstructorsString}
        />
      ))}
    </ListGroup>
  );
}
