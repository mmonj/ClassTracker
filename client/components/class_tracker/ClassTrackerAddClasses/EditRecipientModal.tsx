import React, { useContext, useEffect, useRef, useState } from "react";

import { Button, Modal, Placeholder } from "react-bootstrap";

import { CSRFToken, Context, interfaces, reverse, templates } from "@reactivated";

import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { useFetch } from "@client/hooks/useFetch";
import { fetchByReactivated } from "@client/utils";

import { AnimatePresence, motion } from "framer-motion";

import { FormFieldset } from "../../forms/FormFieldset";

interface Props {
  show: boolean;
  editingRecipientId: number | null;
  onHide: () => void;
  setRecipients: React.Dispatch<
    React.SetStateAction<templates.ClassTrackerAddClasses["recipients"]>
  >;
}

export function EditRecipientModal({ show, editingRecipientId, onHide, setRecipients }: Props) {
  const [recipientForm, setRecipientForm] = useState<
    interfaces.RespGetRecipientForm["recipient_form"] | null
  >(null);
  const [contactInfoForms, setContactInfoForms] = useState<
    interfaces.RespGetRecipientForm["contact_info_forms"]
  >([]);
  const [newContactInfoForm, setNewContactInfoForm] = useState<
    interfaces.RespGetRecipientForm["contact_info_forms"][number] | null
  >(null);

  const [isNewContactFormShown, setIsNewContactFormShown] = useState(false);

  const getRecipientFormFetcher = useFetch<interfaces.RespGetRecipientForm>();
  const updateRecipientFetcher = useFetch<interfaces.RespEditRecipient>();

  const context = useContext(Context);
  const formRef = useRef<HTMLFormElement>(null);

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

    if (recipientId !== editingRecipientId) {
      console.warn("Fetched form for a different recipient ID than expected:", recipientId);
      return;
    }

    setRecipientForm(result.data.recipient_form);
    setContactInfoForms(result.data.contact_info_forms);
    setNewContactInfoForm(result.data.new_contact_info_form);
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

    if (result.data.recipient !== null) {
      if (editingRecipientId === 0) {
        // add new recipient - add empty watched_sections array for template compatibility
        const newRecipient = { ...result.data.recipient, watched_sections: [] };
        setRecipients((prevRecipients) => [newRecipient, ...prevRecipients]);
      } else {
        // update existing recipient
        setRecipients((prevRecipients) =>
          prevRecipients.map((recipient) =>
            recipient.id === editingRecipientId
              ? { ...recipient, ...result.data.recipient }
              : recipient,
          ),
        );
      }

      setRecipientForm(null);
      setContactInfoForms([]);
      onHide();
    }
  }

  useEffect(() => {
    if (editingRecipientId === null) {
      // clear state when modal is closed
      setRecipientForm(null);
      setContactInfoForms([]);
      setNewContactInfoForm(null);
      setIsNewContactFormShown(false);
      return;
    }

    console.log("Editing recipient ID:", editingRecipientId);

    // clear existing state before fetching new data
    setRecipientForm(null);
    setContactInfoForms([]);
    setNewContactInfoForm(null);
    setIsNewContactFormShown(false);

    void handleFetchRecipientForm(editingRecipientId);
  }, [editingRecipientId]);

  return (
    <Modal show={show} backdrop="static" onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>
          {editingRecipientId === 0 ? "Add New Recipient" : "Edit Recipient"}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <>
          {getRecipientFormFetcher.errorMessages.length > 0 && (
            <div className="alert alert-danger mb-3" role="alert">
              <strong>Error:</strong>
              <ul className="mb-0 mt-2">
                {getRecipientFormFetcher.errorMessages.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          )}
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
          {recipientForm !== null && newContactInfoForm !== null && (
            <form onSubmit={handleFormSubmit} ref={formRef}>
              <CSRFToken />
              <FormFieldset form={recipientForm} />
              {contactInfoForms.map((form, index) => (
                <FormFieldset key={index} form={form} />
              ))}

              <AnimatePresence mode="wait">
                {!isNewContactFormShown ? (
                  <motion.div
                    key="add-button"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.15, ease: "easeInOut" }}
                    className="mb-3"
                  >
                    <Button
                      variant="outline-primary"
                      size="sm"
                      onClick={() => setIsNewContactFormShown(true)}
                    >
                      <FontAwesomeIcon icon={faPlus} className="me-2" />
                      Add new contact info
                    </Button>
                  </motion.div>
                ) : (
                  <motion.div
                    key="contact-form"
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    transition={{ duration: 0.15, ease: "easeOut" }}
                  >
                    <FormFieldset form={newContactInfoForm} />
                  </motion.div>
                )}
              </AnimatePresence>
            </form>
          )}
        </>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button type="button" variant="primary" onClick={() => formRef.current?.requestSubmit()}>
          {editingRecipientId === 0 ? "Add Recipient" : "Save Changes"}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
