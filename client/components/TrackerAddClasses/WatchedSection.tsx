import React from "react";

import { Button } from "react-bootstrap";

import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

interface CourseSection {
  id: number;
  number: number;
  topic: string;
  course: {
    id: number;
    code: string;
    level: string;
  };
}

interface Props {
  section: CourseSection;
  onRemove: (sectionId: number) => void;
}

export function WatchedSection({ section, onRemove }: Props) {
  return (
    <li className="mb-2">
      <div className="d-flex justify-content-between align-items-start">
        <div className="flex-grow-1">
          <div className="d-flex align-items-center gap-2 mb-1">
            <strong>
              {section.course.code} {section.course.level}
            </strong>
            <span className="badge bg-secondary">Section {section.number}</span>
          </div>
          <div className="text-muted small">{section.topic}</div>
        </div>
        <Button
          variant="link"
          size="sm"
          onClick={() => onRemove(section.id)}
          title="Remove watched section"
          style={{ color: "gray" }}
        >
          <FontAwesomeIcon icon={faTimes} />
        </Button>
      </div>
    </li>
  );
}
