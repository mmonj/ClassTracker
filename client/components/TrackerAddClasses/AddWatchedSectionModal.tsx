import React from "react";

import { Button, Form, Modal } from "react-bootstrap";

interface Props {
  show: boolean;
  addingSectionRecipientId: number | null;
  onHide: () => void;
  onSubmit: (e: React.FormEvent) => void;
}

export function AddWatchedSectionModal({
  show,
  addingSectionRecipientId,
  onHide,
  onSubmit,
}: Props) {
  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>Add Watched Section</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={onSubmit}>{/* Form content will be added here */}</Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button type="button" variant="primary" onClick={onSubmit}>
          Add Section
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
