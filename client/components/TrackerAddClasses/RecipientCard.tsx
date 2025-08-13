import React from "react";

import { templates } from "@reactivated";
import { Button } from "react-bootstrap";

import { faEdit, faPlus, faUser } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { WatchedSection } from "./WatchedSection";

type CourseSection = templates.TrackerAddClasses["recipients"][number]["watched_sections"][number];

interface ContactInfo {
  id: number;
  // Add other contact info fields as needed
}

interface Recipient {
  id: number;
  name: string;
  phone_numbers: ContactInfo[];
  watched_sections: CourseSection[];
}

interface Props {
  recipient: Recipient;
  onEdit: (recipientId: number) => void;
  onAddWatchedSection: (recipientId: number) => void;
  onRemoveWatchedSection: (recipientId: number, sectionId: number) => void;
}

export function RecipientCard({
  recipient,
  onEdit,
  onAddWatchedSection,
  onRemoveWatchedSection,
}: Props) {
  return (
    <div className="border rounded p-3 mb-3">
      <div className="d-flex justify-content-between mb-2">
        <div className="d-flex align-items-center gap-2">
          <div className="d-flex gap-2">
            <div>
              <FontAwesomeIcon icon={faUser} className="text-muted" />
            </div>
            <h5 className="mb-0">{recipient.name}</h5>
          </div>
          {recipient.phone_numbers.length > 0 ? (
            <span className="badge bg-info">
              {recipient.phone_numbers.length} contact
              {recipient.phone_numbers.length !== 1 ? "s" : ""}
            </span>
          ) : (
            <span className="badge bg-warning">No contact info</span>
          )}
          <Button
            variant="link"
            size="lg"
            onClick={() => onEdit(recipient.id)}
            title="Edit recipient"
          >
            <FontAwesomeIcon icon={faEdit} />
          </Button>
        </div>
        <Button
          variant="link"
          size="sm"
          onClick={() => onAddWatchedSection(recipient.id)}
          title="Add watched section"
        >
          <FontAwesomeIcon icon={faPlus} />
        </Button>
      </div>

      {recipient.watched_sections.length > 0 ? (
        <div>
          <h6>Watched Sections:</h6>
          <ul className="list-unstyled">
            {recipient.watched_sections.map((section) => (
              <WatchedSection
                key={section.id}
                section={section}
                onRemove={(sectionId) => onRemoveWatchedSection(recipient.id, sectionId)}
              />
            ))}
          </ul>
        </div>
      ) : (
        <p className="text-muted">No watched sections</p>
      )}
    </div>
  );
}
