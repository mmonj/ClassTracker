import React from "react";

import { Button } from "react-bootstrap";

import { templates } from "@reactivated";

import { faEdit, faPlus, faUser } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { AnimatePresence, motion } from "framer-motion";

import { WatchedSection } from "./WatchedSection";

const watchedSectionAnimations = {
  initial: { opacity: 0, height: 0, x: -20 },
  exit: {
    opacity: 0,
    height: 0,
    x: 20,
    transition: {
      duration: 0.3,
      ease: "easeIn" as const,
    },
  },
};

const noSectionsAnimation = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
};

// generate animate prop with stagger delay based on section ID
function getWatchedSectionAnimate(sectionId: number) {
  return {
    opacity: 1,
    height: "auto" as const,
    x: 0,
    transition: {
      duration: 0.4,
      ease: "easeOut" as const,
      delay: (sectionId % 10) * 0.1,
    },
  };
}

type TRecipient = templates.ClassTrackerAddClasses["recipients"][number];

interface Props {
  recipient: TRecipient;
  setRecipients: React.Dispatch<React.SetStateAction<TRecipient[]>>;
  onEdit: (recipientId: number) => void;
  onAddWatchedSection: (recipientId: number) => void;
}

export function RecipientCard({ recipient, setRecipients, onEdit, onAddWatchedSection }: Props) {
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
            <AnimatePresence mode="popLayout">
              {recipient.watched_sections.map((section) => (
                <motion.li
                  key={section.id}
                  initial={watchedSectionAnimations.initial}
                  animate={getWatchedSectionAnimate(section.id)}
                  exit={watchedSectionAnimations.exit}
                  layout
                  style={{ overflow: "hidden" }}
                >
                  <WatchedSection
                    section={section}
                    recipientId={recipient.id}
                    setRecipients={setRecipients}
                  />
                </motion.li>
              ))}
            </AnimatePresence>
          </ul>
        </div>
      ) : (
        <motion.p
          initial={noSectionsAnimation.initial}
          animate={noSectionsAnimation.animate}
          className="text-muted"
        >
          No watched sections
        </motion.p>
      )}
    </div>
  );
}
