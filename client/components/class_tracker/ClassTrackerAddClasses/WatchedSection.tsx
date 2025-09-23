import React, { useContext } from "react";

import { Button, Spinner } from "react-bootstrap";

import { Context, interfaces, reverse, templates } from "@reactivated";

import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { useFetch } from "@client/hooks/useFetch";
import { fetchByReactivated } from "@client/utils";

interface Props {
  section: templates.ClassTrackerAddClasses["recipients"][number]["watched_sections"][number];
  recipientId: number;
  setRecipients: React.Dispatch<
    React.SetStateAction<templates.ClassTrackerAddClasses["recipients"]>
  >;
}

export function WatchedSection({ section, recipientId, setRecipients }: Props) {
  const context = useContext(Context);
  const removeWatchedSectionFetcher = useFetch<interfaces.BasicResponse>();

  const instructorNames = section.instruction_entries
    .map((entry) => entry.instructor.name)
    .join(", ");

  async function handleRemoveSection() {
    const confirmed = window.confirm(
      `Are you sure you want to remove "${section.course.code} ${section.course.level} - Section ${section.number} (${instructorNames})" from watched sections?`,
    );

    if (!confirmed) {
      return;
    }

    console.log("Removing watched section:", section.id, "from recipient:", recipientId);

    const result = await removeWatchedSectionFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("class_tracker:remove_watched_section", {
          recipient_id: recipientId,
          section_id: section.id,
        }),
        context.csrf_token,
        "POST",
      ),
    );

    if (!result.ok) {
      console.error("Failed to remove watched section:", result.errors);
      return;
    }

    // remove the section from the corresponding recipient
    setRecipients((prevRecipients) =>
      prevRecipients.map((r) =>
        r.id === recipientId
          ? {
              ...r,
              watched_sections: r.watched_sections.filter((s) => s.id !== section.id),
            }
          : r,
      ),
    );
  }
  return (
    <div className="mb-2">
      <div className="d-flex justify-content-between align-items-start">
        <div className="flex-grow-1">
          <div className="d-flex align-items-center gap-2 mb-1">
            <strong>
              {section.course.code} {section.course.level}
            </strong>
            <span className="badge bg-secondary">Section {section.number}</span>
          </div>
          <div className="text-muted small">{section.topic}</div>
          {section.instruction_entries.length > 0 && (
            <div className="text-muted small">
              <strong>Instructor(s):</strong> {instructorNames}
            </div>
          )}
        </div>
        <Button
          variant="link"
          size="sm"
          onClick={handleRemoveSection}
          title="Remove watched section"
          disabled={removeWatchedSectionFetcher.isLoading}
          style={{ color: "gray" }}
        >
          {removeWatchedSectionFetcher.isLoading ? (
            <Spinner animation="border" size="sm" />
          ) : (
            <FontAwesomeIcon icon={faTimes} />
          )}
        </Button>
      </div>
    </div>
  );
}
