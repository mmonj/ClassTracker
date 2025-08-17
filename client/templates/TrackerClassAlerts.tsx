import React, { useEffect, useMemo, useState } from "react";

import { templates } from "@reactivated";
import { Alert, Card } from "react-bootstrap";
import { SingleValue } from "react-select";

import { Navbar } from "@client/components/class_tracker/Navbar";
import {
  AlertsFilters,
  AlertsList,
  AlertsPagination,
} from "@client/components/class_tracker/TrackerClassAlerts";
import { Layout } from "@client/layouts/Layout";

interface RecipientOption {
  value: number;
  label: string;
}

export function Template(props: templates.TrackerClassAlerts) {
  const [filterText, setFilterText] = useState("");
  const [debouncedFilterText, setDebouncedFilterText] = useState("");

  useEffect(() => {
    const delay = filterText.trim() === "" ? 0 : 300;
    const timer = setTimeout(() => {
      setDebouncedFilterText(filterText);
    }, delay);

    return () => clearTimeout(timer);
  }, [filterText]);

  const [selectedRecipient] = useState<RecipientOption | null>(
    props.selected_recipient_id > 0
      ? {
          value: props.selected_recipient_id,
          label:
            props.recipients.find((r) => r.id === props.selected_recipient_id)?.name ?? "Unknown",
        }
      : null,
  );

  const recipientOptions = useMemo(
    () => [
      { value: 0, label: "All Recipients" },
      ...props.recipients.map((recipient) => ({
        value: recipient.id,
        label: recipient.name,
      })),
    ],
    [props.recipients],
  ) satisfies RecipientOption[];

  // filter alerts based on search text
  const filteredAlerts = useMemo(
    () =>
      props.class_alerts.filter((alert) => {
        if (!debouncedFilterText.trim()) return true;

        const searchText = debouncedFilterText.toLowerCase();
        const alertText = [
          alert.recipient.name,
          alert.course_section.course.code,
          alert.course_section.course.level,
          alert.course_section.number.toString(),
          alert.course_section.course.subject.name,
          alert.course_section.term.full_term_name,
          alert.course_section.topic,
          getDaysAndTimesString(alert.course_section.instruction_entries),
          getInstructorsString(alert.course_section.instruction_entries),
        ]
          .join(" ")
          .toLowerCase();

        return alertText.includes(searchText);
      }),
    [props.class_alerts, debouncedFilterText],
  );

  function handleFilterChange(event: React.ChangeEvent<HTMLInputElement>) {
    setFilterText(event.target.value);
  }

  function handleClearFilter() {
    setFilterText("");
  }

  function handleRecipientChange(option: SingleValue<RecipientOption>) {
    if (!option) return;

    // create URL with recipient filter
    const url = new URL(window.location.href);
    if (option.value === 0) {
      url.searchParams.delete("recipient_id");
    } else {
      url.searchParams.set("recipient_id", option.value.toString());
    }

    // make sure to reset to first page when filtering
    url.searchParams.delete("page");

    window.location.href = url.toString();
  }

  function getInstructorsString(
    instructionEntries: templates.TrackerClassAlerts["class_alerts"][0]["course_section"]["instruction_entries"],
  ): string {
    const instructors = instructionEntries
      .map((entry) => entry.instructor.name)
      .filter((name, index, array) => array.indexOf(name) === index); // remove duplicates
    return instructors.join(", ");
  }

  function getDaysAndTimesString(
    instructionEntries: templates.TrackerClassAlerts["class_alerts"][0]["course_section"]["instruction_entries"],
  ): string {
    const daysAndTimes = instructionEntries
      .map((entry) => entry.get_days_and_times)
      .filter((daysAndTimes, index, array) => array.indexOf(daysAndTimes) === index); // remove duplicates
    return daysAndTimes.join("; ");
  }

  function formatDateTime(dateTime: string): string {
    return new Date(dateTime).toLocaleString();
  }

  function generatePaginationUrl(page: number): string {
    const url = new URL(window.location.href);
    url.searchParams.set("page", page.toString());
    return url.toString();
  }

  return (
    <Layout title={props.title} Navbar={Navbar}>
      <Card className="mb-4">
        <Card.Header>
          <Card.Title className="mb-0">Class Alerts</Card.Title>
        </Card.Header>
        <Card.Body>
          <AlertsFilters
            selectedRecipient={selectedRecipient}
            recipientOptions={recipientOptions}
            filterText={filterText}
            onRecipientChange={handleRecipientChange}
            onFilterChange={handleFilterChange}
            onClearFilter={handleClearFilter}
          />

          {filteredAlerts.length === 0 ? (
            <Alert variant="info">
              {props.class_alerts.length === 0
                ? `No class alerts found${props.selected_recipient_id > 0 ? " for the selected recipient" : ""}.`
                : `No alerts match the current search filter "${debouncedFilterText}".`}
            </Alert>
          ) : (
            <>
              {debouncedFilterText.trim() && (
                <div className="mb-3">
                  <small className="text-muted">
                    Showing {filteredAlerts.length} of {props.class_alerts.length} alerts
                  </small>
                </div>
              )}

              <AlertsList
                alerts={filteredAlerts}
                formatDateTime={formatDateTime}
                getDaysAndTimesString={getDaysAndTimesString}
                getInstructorsString={getInstructorsString}
              />

              <AlertsPagination
                pagination={props.pagination}
                generatePaginationUrl={generatePaginationUrl}
              />
            </>
          )}
        </Card.Body>
      </Card>
    </Layout>
  );
}
