import React, { useContext, useState } from "react";

import { Context, interfaces, templates } from "@reactivated";
import { Button, Card } from "react-bootstrap";

import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { AnimatePresence, motion } from "framer-motion";

import { Navbar } from "@client/components/Navbar";
import {
  AddWatchedSectionModal,
  EditRecipientModal,
  RecipientCard,
} from "@client/components/TrackerAddClasses";
import { useFetch } from "@client/hooks/useFetch";
import { Layout } from "@client/layouts/Layout";

const recipientCardAnimations = {
  initial: { opacity: 0, y: 30, scale: 0.95 },
  exit: {
    opacity: 0,
    y: -20,
    scale: 0.95,
    transition: {
      duration: 0.3,
      ease: "easeIn" as const,
    },
  },
};

const noRecipientsAnimation = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
};

// generate animate prop with stagger delay based on recipient ID
const getRecipientCardAnimate = (recipientId: number) => ({
  opacity: 1,
  y: 0,
  scale: 1,
  transition: {
    duration: 0.3,
    ease: "easeOut" as const,
    delay: (recipientId % 10) * 0.1,
  },
});

export function Template(props: templates.TrackerAddClasses) {
  const [recipients, setRecipients] = useState(props.recipients);
  const [showEditRecipientModal, setShowEditRecipientModal] = useState(false);
  const [editingRecipientId, setEditingRecipientId] = useState<number | null>(null);

  const [showAddSectionModal, setShowAddSectionModal] = useState(false);
  const [addingSectionRecipientId, setAddingSectionRecipientId] = useState<number | null>(null);

  // const updateRecipientFetcher = useFetch<interfaces.RespEditRecipient>();
  const addWatchedSectionFetcher = useFetch<interfaces.RespAddWatchedSection>();

  const context = useContext(Context);

  function handleAddWatchedSection(recipientId: number) {
    setAddingSectionRecipientId(recipientId);
    setShowAddSectionModal(true);
  }

  function handleCloseAddSectionModal() {
    setShowAddSectionModal(false);
    setAddingSectionRecipientId(null);
  }

  function handleAddSectionSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (addingSectionRecipientId !== null) {
      handleAddSection(addingSectionRecipientId);
    }
    handleCloseAddSectionModal();
  }

  function handleAddSection(sectionId: number) {
    // TODO: Implement add watched section functionality
    console.log("Add watched section:", sectionId);
  }

  function handleShowEditRecipientModal(recipientId: number) {
    setEditingRecipientId(recipientId);
    setShowEditRecipientModal(true);
  }

  function handleShowAddRecipientModal() {
    setEditingRecipientId(0); // Sentinel value for new recipient
    setShowEditRecipientModal(true);
  }

  function handleCloseEditRecipientModal() {
    setShowEditRecipientModal(false);
    setEditingRecipientId(null);
  }

  function handleEditRecipientSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (editingRecipientId !== null) {
      handleEditRecipient(editingRecipientId);
    }
    handleCloseEditRecipientModal();
  }

  function handleEditRecipient(recipientId: number) {
    // TODO: Implement edit recipient functionality
    console.log("Edit recipient:", recipientId);
  }

  return (
    <Layout title="Watched Sections" Navbar={Navbar}>
      <Card>
        <Card.Title className="p-3">
          <div className="d-flex justify-content-between align-items-center">
            <h3>Recipients</h3>
            <Button variant="primary" size="sm" onClick={handleShowAddRecipientModal}>
              <FontAwesomeIcon icon={faPlus} className="me-2" />
              Add New Recipient
            </Button>
          </div>
        </Card.Title>
        <Card.Body>
          <AnimatePresence mode="popLayout">
            {recipients.map((recipient) => (
              <motion.div
                key={recipient.id}
                initial={recipientCardAnimations.initial}
                animate={getRecipientCardAnimate(recipient.id)}
                exit={recipientCardAnimations.exit}
                layout
                style={{ originY: 0 }}
              >
                <RecipientCard
                  recipient={recipient}
                  setRecipients={setRecipients}
                  onEdit={handleShowEditRecipientModal}
                  onAddWatchedSection={handleAddWatchedSection}
                />
              </motion.div>
            ))}
          </AnimatePresence>

          {recipients.length === 0 && (
            <motion.p
              initial={noRecipientsAnimation.initial}
              animate={noRecipientsAnimation.animate}
              className="text-muted"
            >
              No recipients found
            </motion.p>
          )}
        </Card.Body>
      </Card>

      <EditRecipientModal
        show={showEditRecipientModal}
        editingRecipientId={editingRecipientId}
        onHide={handleCloseEditRecipientModal}
        setRecipients={setRecipients}
      />

      <AddWatchedSectionModal
        show={showAddSectionModal}
        addingSectionRecipientId={addingSectionRecipientId}
        onHide={handleCloseAddSectionModal}
        onSubmit={handleAddSectionSubmit}
      />
    </Layout>
  );
}
