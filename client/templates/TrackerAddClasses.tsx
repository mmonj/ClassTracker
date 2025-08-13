import React, { useContext, useState } from "react";

import { Context, interfaces, templates } from "@reactivated";
import { Card } from "react-bootstrap";

import { Navbar } from "@client/components/Navbar";
import {
  AddWatchedSectionModal,
  EditRecipientModal,
  RecipientCard,
} from "@client/components/TrackerAddClasses";
import { useFetch } from "@client/hooks/useFetch";
import { Layout } from "@client/layouts/Layout";

export function Template(props: templates.TrackerAddClasses) {
  const [recipients, setRecipients] = useState(props.recipients);
  const [showEditRecipientModal, setShowEditRecipientModal] = useState(false);
  const [editingRecipientId, setEditingRecipientId] = useState<number | null>(null);

  const [showAddSectionModal, setShowAddSectionModal] = useState(false);
  const [addingSectionRecipientId, setAddingSectionRecipientId] = useState<number | null>(null);

  // const updateRecipientFetcher = useFetch<interfaces.RespEditRecipient>();
  const addWatchedSectionFetcher = useFetch<interfaces.RespAddWatchedSection>();
  const removeWatchedSectionFetcher = useFetch<interfaces.BasicResponse>();

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

  function handleRemoveWatchedSection(recipientId: number, sectionId: number) {
    // TODO: Implement AJAX request to remove watched section
    console.log("Remove watched section:", sectionId, "from recipient:", recipientId);
  }

  function handleShowEditRecipientModal(recipientId: number) {
    setEditingRecipientId(recipientId);
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
          <h3>Recipients</h3>
        </Card.Title>
        <Card.Body>
          {recipients.map((recipient) => (
            <RecipientCard
              key={recipient.id}
              recipient={recipient}
              onEdit={handleShowEditRecipientModal}
              onAddWatchedSection={handleAddWatchedSection}
              onRemoveWatchedSection={handleRemoveWatchedSection}
            />
          ))}

          {recipients.length === 0 && <p className="text-muted">No recipients found</p>}
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
