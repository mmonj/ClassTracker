import React, { useState } from "react";

import { Context, interfaces, reverse } from "@reactivated";
import { Alert, Button, Form, Modal } from "react-bootstrap";
import Select from "react-select";

import { fetchByReactivated } from "@client/utils";

import { useFetch } from "@client/hooks/useFetch";
import { validateAndFetchDiscordInvite } from "@client/utils/discord_tracker/discord-api-fetcher";

interface Props {
  show: boolean;
  onHide: () => void;
}

interface SchoolOption {
  value: number;
  label: string;
}

interface SubjectOption {
  value: number;
  label: string;
}

interface CourseOption {
  value: number;
  label: string;
}

export function AddInviteModal({ show, onHide }: Props) {
  const context = React.useContext(Context);
  const [inviteUrl, setInviteUrl] = useState("");
  const [notes, setNotes] = useState("");
  const [selectedSchool, setSelectedSchool] = useState<SchoolOption | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<SubjectOption | null>(null);
  const [selectedCourse, setSelectedCourse] = useState<CourseOption | null>(null);
  const [showSchoolSelection, setShowSchoolSelection] = useState(false);
  const [guildInfo, setGuildInfo] = useState<{ name: string; id: string } | null>(null);

  // client side validation state
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const schoolsFetcher = useFetch<interfaces.GetAvailableSchoolsResponse>();
  const submitFetcher = useFetch<interfaces.SubmitInviteResponse>();
  const subjectsFetcher = useFetch<interfaces.GetSubjectsResponse>();
  const coursesFetcher = useFetch<interfaces.GetCoursesResponse>();

  const schoolOptions: SchoolOption[] =
    schoolsFetcher.data?.available_schools.map((school) => ({
      value: school.id,
      label: school.name,
    })) ?? [];

  const subjectOptions: SubjectOption[] =
    subjectsFetcher.data?.subjects.map((subject) => ({
      value: subject.id,
      label: subject.name,
    })) ?? [];

  const courseOptions: CourseOption[] =
    coursesFetcher.data?.courses.map((course) => ({
      value: course.id,
      label: `${course.code} ${course.level} - ${course.title}`,
    })) ?? [];

  const handleValidateInvite = async (e: React.FormEvent) => {
    e.preventDefault();

    setIsValidating(true);
    setValidationError(null);

    try {
      const validationResult = await validateAndFetchDiscordInvite(inviteUrl);

      if (!validationResult.isValid) {
        setValidationError(validationResult.error ?? "Failed to validate Discord invite");
        return;
      }

      if (!validationResult.inviteData) {
        setValidationError("No invite data received");
        return;
      }

      // set guild info from discord API response
      setGuildInfo({
        name: validationResult.inviteData.guild.name,
        id: validationResult.inviteData.guild.id,
      });

      // fetch available schools from backend
      const schoolsResult = await schoolsFetcher.fetchData(() =>
        fetchByReactivated(
          reverse("discord_tracker:get_available_schools"),
          context.csrf_token,
          "GET",
        ),
      );

      if (schoolsResult.ok && schoolsResult.data.success) {
        setShowSchoolSelection(true);
      } else {
        setValidationError("Failed to fetch available schools");
      }
    } catch (error) {
      setValidationError(error instanceof Error ? error.message : "Unknown error occurred");
    } finally {
      setIsValidating(false);
    }
  };

  const handleSubmit = async () => {
    if (!guildInfo || !selectedSchool) {
      return;
    }

    const formData = new URLSearchParams({
      invite_url: inviteUrl,
      notes: notes,
      guild_name: guildInfo.name,
      guild_id: guildInfo.id,
      school_id: selectedSchool.value.toString(),
    });

    if (selectedSubject) {
      formData.append("subject_id", selectedSubject.value.toString());
    }

    if (selectedCourse) {
      formData.append("course_id", selectedCourse.value.toString());
    }

    const result = await submitFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("discord_tracker:submit_invite"),
        context.csrf_token,
        "POST",
        formData,
      ),
    );

    if (!result.ok) {
      return;
    }

    setTimeout(() => {
      handleClose();
      window.location.reload(); // refresh to show new server
    }, 2000);
  };

  const handleSchoolChange = async (option: SchoolOption | null) => {
    setSelectedSchool(option);
    setSelectedSubject(null);
    setSelectedCourse(null);

    if (option === null) return;

    await subjectsFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("discord_tracker:get_subjects", { school_id: option.value }),
        context.csrf_token,
        "GET",
      ),
    );
  };

  const handleSubjectChange = async (option: SubjectOption | null) => {
    setSelectedSubject(option);
    setSelectedCourse(null);

    if (option === null || selectedSchool === null) return;

    await coursesFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("discord_tracker:get_courses", {
          school_id: selectedSchool.value,
          subject_id: option.value,
        }),
        context.csrf_token,
        "GET",
      ),
    );
  };

  const handleCourseChange = (option: CourseOption | null) => {
    setSelectedCourse(option);
  };

  const handleClose = () => {
    setInviteUrl("");
    setNotes("");
    setSelectedSchool(null);
    setSelectedSubject(null);
    setSelectedCourse(null);
    setShowSchoolSelection(false);
    setGuildInfo(null);
    setIsValidating(false);
    setValidationError(null);
    onHide();
  };

  return (
    <Modal show={show} onHide={handleClose} centered size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
          {showSchoolSelection
            ? `Associate "${guildInfo?.name}" with Academic Info`
            : "Add Discord Invite"}
        </Modal.Title>
      </Modal.Header>

      <Modal.Body>
        {!showSchoolSelection ? (
          // step 1: invite url validation
          <Form onSubmit={handleValidateInvite}>
            <Form.Group className="mb-3">
              <Form.Label>Discord Invite URL</Form.Label>
              <Form.Control
                type="url"
                placeholder="https://discord.gg/invite-code"
                value={inviteUrl}
                onChange={(e) => setInviteUrl(e.target.value)}
                required
                disabled={isValidating}
              />
              <Form.Text className="text-muted">
                Enter the full Discord invite URL (e.g., https://discord.gg/abc123 or
                https://discord.com/invite/abc123)
              </Form.Text>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Notes (Optional)</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                placeholder="Add any notes about this server (optional)"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                maxLength={511}
                disabled={isValidating}
              />
              <Form.Text className="text-muted">
                Optional notes about the server that will help others understand what it's for
              </Form.Text>
            </Form.Group>

            {validationError !== null && (
              <Alert variant="danger" className="mb-3">
                {validationError}
              </Alert>
            )}

            <div className="d-flex justify-content-end">
              <Button
                variant="secondary"
                onClick={handleClose}
                className="me-2"
                disabled={isValidating}
              >
                Cancel
              </Button>
              <Button variant="primary" type="submit" disabled={!inviteUrl.trim() || isValidating}>
                {isValidating ? "Validating..." : "Next: Select Academic Info"}
              </Button>
            </div>
          </Form>
        ) : (
          // step 2: school/subject/course selection form
          <div>
            <Alert variant="info" className="mb-3">
              <strong>Discord Server Validated!</strong> Please associate this server with your
              academic information.
            </Alert>

            {submitFetcher.data && submitFetcher.errorMessages.length === 0 && (
              <Alert variant="success" className="mb-3">
                Discord server successfully added!
              </Alert>
            )}

            <Form.Group className="mb-3">
              <Form.Label>
                School <span className="text-danger">*</span>
              </Form.Label>
              <Select
                value={selectedSchool}
                onChange={handleSchoolChange}
                options={schoolOptions}
                placeholder="Select a school..."
                isSearchable
                isLoading={schoolsFetcher.isLoading}
                classNamePrefix="react-select"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Subject (Optional)</Form.Label>
              <Select
                value={selectedSubject}
                onChange={handleSubjectChange}
                options={subjectOptions}
                placeholder="Select a subject..."
                isSearchable
                isDisabled={!selectedSchool}
                isLoading={subjectsFetcher.isLoading}
                classNamePrefix="react-select"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Course (Optional)</Form.Label>
              <Select
                value={selectedCourse}
                onChange={handleCourseChange}
                options={courseOptions}
                placeholder="Select a course..."
                isSearchable
                isDisabled={!selectedSubject}
                isLoading={coursesFetcher.isLoading}
                classNamePrefix="react-select"
              />
            </Form.Group>

            {submitFetcher.errorMessages.length > 0 && (
              <Alert variant="danger" className="mb-3">
                {submitFetcher.errorMessages.map((error, index) => (
                  <div key={index}>{error}</div>
                ))}
              </Alert>
            )}

            <div className="d-flex justify-content-end">
              <Button
                variant="secondary"
                onClick={() => setShowSchoolSelection(false)}
                className="me-2"
                disabled={submitFetcher.isLoading}
              >
                Back
              </Button>
              <Button
                variant="primary"
                onClick={handleSubmit}
                disabled={!selectedSchool || submitFetcher.isLoading}
              >
                {submitFetcher.isLoading ? "Submitting..." : "Submit Invite"}
              </Button>
            </div>
          </div>
        )}
      </Modal.Body>
    </Modal>
  );
}
