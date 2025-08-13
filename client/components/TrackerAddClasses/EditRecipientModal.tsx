import React, { useContext, useEffect, useState } from "react";

import { CSRFToken, Context, interfaces, reverse, templates } from "@reactivated";
import { Button, Modal, Placeholder } from "react-bootstrap";

import { fetchByReactivated } from "@client/utils";

import { useFetch } from "@client/hooks/useFetch";

import { FormBody } from "../forms/FormBody";

interface Props {
  show: boolean;
  editingRecipientId: number | null;
  onHide: () => void;
  setRecipients: React.Dispatch<React.SetStateAction<templates.TrackerAddClasses["recipients"]>>;
}

export function EditRecipientModal({ show, editingRecipientId, onHide, setRecipients }: Props) {
  const [recipientForm, setRecipientForm] = useState<
    interfaces.RespGetRecipientForm["recipient_form"] | null
  >(null);
  const [contactInfoForms, setContactInfoForms] = useState<
    interfaces.RespGetRecipientForm["contact_info_forms"]
  >([]);
  const getRecipientFormFetcher = useFetch<interfaces.RespGetRecipientForm>();
  const updateRecipientFetcher = useFetch<interfaces.RespEditRecipient>();

  const context = useContext(Context);
  const formSubmitRef = React.useRef<HTMLInputElement>(null);

  async function handleFetchRecipientForm(recipientId: number | null) {
    if (recipientId === null) return;

    console.log("Fetching recipient form for ID:", recipientId);

    const result = await getRecipientFormFetcher.fetchData(() => {
      return fetchByReactivated(
        reverse("class_tracker:get_recipient_form", { recipient_id: recipientId }),
        context.csrf_token,
        "GET",
      );
    });

    if (!result.ok) {
      console.error("Error fetching recipient form:", result.errors);
      return;
    }

    // Only update state if we're still editing the same recipient
    // This prevents race conditions when switching between recipients quickly
    if (recipientId === editingRecipientId) {
      setRecipientForm(result.data.recipient_form);
      setContactInfoForms(result.data.contact_info_forms);
    }
  }

  async function handleFormSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (editingRecipientId === null) return;

    console.log("Submitting form for recipient ID:", editingRecipientId);

    const result = await updateRecipientFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("class_tracker:update_recipient", { recipient_id: editingRecipientId }),
        context.csrf_token,
        "POST",
        new FormData(e.target as HTMLFormElement),
      ),
    );

    if (!result.ok) {
      console.error("Result not ok. Errors:", result.errors);
      return;
    }

    console.log(result.data);

    if (result.data.recipient_form && result.data.contact_info_forms !== null) {
      setRecipientForm(result.data.recipient_form);
      setContactInfoForms(result.data.contact_info_forms);
      return;
    }

    if (result.data.recipient && result.data.contact_infos !== null) {
      setRecipients((prevRecipients) =>
        prevRecipients.map((recipient) =>
          recipient.id === editingRecipientId
            ? { ...recipient, ...result.data.recipient }
            : recipient,
        ),
      );

      setRecipientForm(null);
      setContactInfoForms([]);
      onHide();
    }
  }

  useEffect(() => {
    if (editingRecipientId === null) {
      // Clear state when modal is closed
      setRecipientForm(null);
      setContactInfoForms([]);
      return;
    }

    console.log("Editing recipient ID:", editingRecipientId);

    // Clear existing state before fetching new data
    setRecipientForm(null);
    setContactInfoForms([]);

    void handleFetchRecipientForm(editingRecipientId);
  }, [editingRecipientId]);

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>Edit Recipient</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <>
          {getRecipientFormFetcher.isLoading && (
            <>
              <Placeholder animation="glow">
                <Placeholder xs={6} />
              </Placeholder>
              <Placeholder animation="glow">
                <Placeholder xs={7} /> <Placeholder xs={4} /> <Placeholder xs={4} />{" "}
                <Placeholder xs={6} /> <Placeholder xs={8} />
              </Placeholder>
            </>
          )}
          {recipientForm !== null && (
            <form onSubmit={handleFormSubmit}>
              <CSRFToken />
              <FormBody form={recipientForm} />
              {contactInfoForms.map((form, index) => (
                <FormBody key={index} form={form} />
              ))}
              <input type="submit" className="d-none" ref={formSubmitRef} />
            </form>
          )}
        </>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button type="button" variant="primary" onClick={() => formSubmitRef.current?.click()}>
          Save Changes
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
