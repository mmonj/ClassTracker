import React, { useContext, useEffect, useState } from "react";

import { Context, interfaces, reverse, templates } from "@reactivated";
import { Alert, Button, Form, Modal, Spinner } from "react-bootstrap";
import Select, { SingleValue } from "react-select";

import { fetchByReactivated } from "@client/utils";

import { useFetch } from "@client/hooks/useFetch";

interface SchoolOption {
  value: number;
  label: string;
}

interface TermOption {
  value: number;
  label: string;
}

interface SubjectOption {
  value: number;
  label: string;
}

interface SectionOption {
  value: number;
  label: string;
}

const REACT_SELECT_PREFIX = "react-select";

interface Props {
  show: boolean;
  addingSectionRecipientId: number | null;
  termsAvailable: templates.ClassTrackerAddClasses["terms_available"];
  setRecipients: React.Dispatch<
    React.SetStateAction<templates.ClassTrackerAddClasses["recipients"]>
  >;
  onHide: () => void;
}

export function AddWatchedSectionModal({
  show,
  addingSectionRecipientId,
  termsAvailable,
  setRecipients,
  onHide,
}: Props) {
  const [selectedSchool, setSelectedSchool] = useState<SchoolOption | null>(null);
  const [selectedTerm, setSelectedTerm] = useState<TermOption | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<SubjectOption | null>(null);
  const [selectedSection, setSelectedSection] = useState<SectionOption | null>(null);

  const [schools, setSchools] = useState<SchoolOption[]>([]);
  const [subjects, setSubjects] = useState<SubjectOption[]>([]);
  const [sections, setSections] = useState<SectionOption[]>([]);

  const schoolsFetcher = useFetch<interfaces.RespGetSchools>();
  const subjectsFetcher = useFetch<interfaces.RespGetSubjects>();
  const sectionsFetcher = useFetch<interfaces.RespGetCourseSections>();
  const addSectionFetcher = useFetch<interfaces.RespAddWatchedSection>();

  const context = useContext(Context);

  useEffect(() => {
    if (!show) return;

    async function fetchSchools() {
      const result = await schoolsFetcher.fetchData(() =>
        fetchByReactivated(reverse("class_tracker:get_schools"), context.csrf_token, "GET"),
      );

      if (result.ok) {
        const schoolOptions: SchoolOption[] = result.data.schools.map((school) => ({
          value: school.id,
          label: school.name,
        }));
        setSchools(schoolOptions);
      }
    }

    void fetchSchools();
  }, [show]);

  const termOptions = termsAvailable.map((term) => ({
    value: term.id,
    label: term.full_term_name,
  })) satisfies TermOption[];

  function handleSchoolChange(option: SingleValue<SchoolOption>) {
    setSelectedSchool(option);
    setSelectedTerm(null);
    setSelectedSubject(null);
    setSelectedSection(null);
    setSubjects([]);
    setSections([]);
  }

  async function handleTermChange(option: SingleValue<TermOption>) {
    setSelectedTerm(option);
    setSelectedSubject(null);
    setSelectedSection(null);
    setSubjects([]);
    setSections([]);

    if (!option || !selectedSchool) return;

    // get subjects for the selected school and term
    const result = await subjectsFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("class_tracker:get_subjects", {
          school_id: selectedSchool.value,
          term_id: option.value,
        }),
        context.csrf_token,
        "GET",
      ),
    );

    if (result.ok) {
      const responseData = result.data;
      const subjectOptions: SubjectOption[] = responseData.subjects.map((subject) => ({
        value: subject.id,
        label: subject.name,
      }));
      setSubjects(subjectOptions);
    }
  }

  async function handleSubjectChange(option: SingleValue<SubjectOption>) {
    setSelectedSubject(option);
    setSelectedSection(null);
    setSections([]);

    if (!option || !selectedTerm) return;

    const result = await sectionsFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("class_tracker:get_course_sections", {
          term_id: selectedTerm.value,
          subject_id: option.value,
        }),
        context.csrf_token,
        "GET",
      ),
    );

    if (result.ok) {
      try {
        const responseData = result.data;
        const sectionOptions: SectionOption[] = responseData.sections.map((section) => {
          // instructors comma-separated string
          const instructors =
            section.instruction_entries.map((entry) => entry.instructor.name).join(", ") || "";
          const instructorsText =
            instructors.length > 0 ? `(${instructors})` : "(no instructor found)";

          return {
            value: section.id,
            label: `${section.course.code} ${section.course.level} - ${section.topic} ${instructorsText}`,
          };
        });
        setSections(sectionOptions);
      } catch (error) {
        console.error("Error processing sections:", error);
      }
    }
  }

  function handleSectionChange(option: SingleValue<SectionOption>) {
    setSelectedSection(option);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (addingSectionRecipientId === null || addingSectionRecipientId === 0 || !selectedSection)
      return;

    const result = await addSectionFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("class_tracker:add_watched_section", {
          recipient_id: addingSectionRecipientId,
          section_id: selectedSection.value,
        }),
        context.csrf_token,
        "POST",
      ),
    );

    if (result.ok) {
      // update recipients state with the new watched section
      setRecipients((prevRecipients) =>
        prevRecipients.map((recipient) =>
          recipient.id === addingSectionRecipientId
            ? {
                ...recipient,
                watched_sections: [...recipient.watched_sections, result.data.added_section],
              }
            : recipient,
        ),
      );

      onHide();
    }
  }

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Add Watched Section</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Select School</Form.Label>
            {schoolsFetcher.isLoading ? (
              <div className="d-flex align-items-center">
                <Spinner animation="border" size="sm" className="me-2" />
                <span>Loading schools...</span>
              </div>
            ) : (
              <Select<SchoolOption>
                value={selectedSchool}
                onChange={handleSchoolChange}
                options={schools}
                placeholder="Choose a school..."
                isDisabled={subjectsFetcher.isLoading}
                classNamePrefix={REACT_SELECT_PREFIX}
              />
            )}
          </Form.Group>

          {selectedSchool && (
            <Form.Group className="mb-3">
              <Form.Label>Select Term</Form.Label>
              <Select<TermOption>
                value={selectedTerm}
                onChange={handleTermChange}
                options={termOptions}
                placeholder="Choose a term..."
                isDisabled={subjectsFetcher.isLoading}
                classNamePrefix={REACT_SELECT_PREFIX}
              />
            </Form.Group>
          )}

          {selectedTerm && (
            <Form.Group className="mb-3">
              <Form.Label>Select Subject</Form.Label>
              {subjectsFetcher.isLoading ? (
                <div className="d-flex align-items-center">
                  <Spinner animation="border" size="sm" className="me-2" />
                  <span>Loading subjects...</span>
                </div>
              ) : (
                <Select<SubjectOption>
                  value={selectedSubject}
                  onChange={handleSubjectChange}
                  options={subjects}
                  placeholder="Choose a subject..."
                  isDisabled={sectionsFetcher.isLoading}
                  classNamePrefix={REACT_SELECT_PREFIX}
                />
              )}
            </Form.Group>
          )}

          {selectedSubject && (
            <Form.Group className="mb-3">
              <Form.Label>Select Course Section</Form.Label>
              {sectionsFetcher.isLoading ? (
                <div className="d-flex align-items-center">
                  <Spinner animation="border" size="sm" className="me-2" />
                  <span>Loading course sections...</span>
                </div>
              ) : (
                <Select<SectionOption>
                  value={selectedSection}
                  onChange={handleSectionChange}
                  options={sections}
                  placeholder="Choose a course section..."
                  isDisabled={addSectionFetcher.isLoading}
                  classNamePrefix={REACT_SELECT_PREFIX}
                />
              )}
            </Form.Group>
          )}

          {addSectionFetcher.errorMessages.length > 0 && (
            <Alert variant="danger">
              {addSectionFetcher.errorMessages.map((error, index) => (
                <div key={index}>{error}</div>
              ))}
            </Alert>
          )}
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide} disabled={addSectionFetcher.isLoading}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handleSubmit}
          disabled={!selectedSection || addSectionFetcher.isLoading}
        >
          {addSectionFetcher.isLoading ? (
            <>
              <Spinner animation="border" size="sm" className="me-2" />
              Adding...
            </>
          ) : (
            "Add Section"
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
