import React, { useState } from "react";

import { Context, interfaces, reverse } from "@reactivated";
import { Alert, Button, Form, Modal } from "react-bootstrap";
import Select from "react-select";

import { fetchByReactivated } from "@client/utils";

import { useFetch } from "@client/hooks/useFetch";

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

interface InstructorOption {
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
  const [selectedInstructors, setSelectedInstructors] = useState<InstructorOption[]>([]);
  const [showSchoolSelection, setShowSchoolSelection] = useState(false);
  const [guildInfo, setGuildInfo] = useState<{ name: string; id: string } | null>(null);
  const [isPublic, setIsPublic] = useState(false);
  const [availableSchools, setAvailableSchools] = useState<SchoolOption[]>([]);

  // client side validation state
  const [isValidating, setIsValidating] = useState(false);

  const discordUser = context.user.discord_user;
  const isManager = discordUser?.is_manager === true;

  const inviteValidationFetcher = useFetch<interfaces.ValidateDiscordInviteResponse>();
  const submitInviteFetcher = useFetch<interfaces.SubmitInviteResponse>();
  const subjectsFetcher = useFetch<interfaces.GetSubjectsResponse>();
  const coursesFetcher = useFetch<interfaces.GetCoursesResponse>();
  const instructorsFetcher = useFetch<interfaces.GetInstructorsResponse>();

  const schoolOptions: SchoolOption[] = availableSchools;

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

  const instructorOptions: InstructorOption[] =
    instructorsFetcher.data?.instructors.map((instructor) => ({
      value: instructor.id,
      label: instructor.name,
    })) ?? [];

  async function handleDirectSubmit(
    guildInfo: { id: string; name: string; icon_url: string },
    existingServerInfo: NonNullable<
      interfaces.ValidateDiscordInviteResponse["existing_server_info"]
    >,
  ) {
    const formData = new URLSearchParams({
      invite_url: inviteUrl,
      notes: notes,
      guild_name: guildInfo.name,
      guild_id: guildInfo.id,
      // use existing server's first school (required field)
      school_id:
        existingServerInfo.schools.length > 0 ? existingServerInfo.schools[0].id.toString() : "",
      // use existing server's privacy level
      privacy_level: existingServerInfo.privacy_level_info.value,
    });

    // add subject if exists
    if (existingServerInfo.subjects.length > 0) {
      formData.append("subject_id", existingServerInfo.subjects[0].id.toString());
    }

    // add course if exists
    if (existingServerInfo.courses.length > 0) {
      formData.append("course_id", existingServerInfo.courses[0].id.toString());
    }

    const result = await submitInviteFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("discord_tracker:submit_invite"),
        context.csrf_token,
        "POST",
        formData,
      ),
    );

    if (result.ok) {
      setTimeout(() => {
        handleClose();
        window.location.reload();
      }, 100);
    }
  }

  async function handleValidateInvite(e: React.FormEvent) {
    e.preventDefault();

    setIsValidating(true);

    try {
      const formData = new URLSearchParams({
        invite_url: inviteUrl,
      });

      const validationResult = await inviteValidationFetcher.fetchData(() =>
        fetchByReactivated(
          reverse("discord_tracker:validate_discord_invite"),
          context.csrf_token,
          "POST",
          formData,
        ),
      );

      if (!validationResult.ok) {
        // useFetch will automatically handle and display errors
        return;
      }

      const { guild_info, existing_server_info, is_new_server, available_schools } =
        validationResult.data;

      if (!guild_info) {
        // ideally shoulnd't happen
        return;
      }

      // set guild info from backend response
      setGuildInfo({
        name: guild_info.name,
        id: guild_info.id,
      });

      // if server already exists, submit invite directly without step 2
      if (!is_new_server && existing_server_info) {
        await handleDirectSubmit(
          {
            id: guild_info.id,
            name: guild_info.name,
            icon_url: guild_info.icon_url,
          },
          existing_server_info,
        );
        return;
      }

      // server is new, populate schools dropdown and show step 2 for configuration
      setAvailableSchools(
        available_schools.map((school) => ({
          value: school.id,
          label: school.name,
        })),
      );
      setShowSchoolSelection(true);
    } catch {
      // useFetch will handle errors automatically
    } finally {
      setIsValidating(false);
    }
  }

  async function handleSubmit() {
    if (!guildInfo || !selectedSchool) {
      return;
    }

    const formData = new URLSearchParams({
      invite_url: inviteUrl,
      notes: notes,
      guild_name: guildInfo.name,
      guild_id: guildInfo.id,
      school_id: selectedSchool.value.toString(),
      privacy_level: isPublic ? "public" : "private",
    });

    if (selectedSubject) {
      formData.append("subject_id", selectedSubject.value.toString());
    }

    if (selectedCourse) {
      formData.append("course_id", selectedCourse.value.toString());
    }

    // add instructor ids if any are selected
    selectedInstructors.forEach((instructor) => {
      formData.append("instructor_ids", instructor.value.toString());
    });

    const result = await submitInviteFetcher.fetchData(() =>
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
      window.location.reload(); // refresh page
    }, 100);
  }

  async function handleSchoolChange(option: SchoolOption | null) {
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
  }

  async function handleSubjectChange(option: SubjectOption | null) {
    setSelectedSubject(option);
    setSelectedCourse(null);
    setSelectedInstructors([]);

    if (option === null || selectedSchool === null) return;

    // fetch both courses and instructors when subject changes
    await Promise.all([
      coursesFetcher.fetchData(() =>
        fetchByReactivated(
          reverse("discord_tracker:get_courses", {
            school_id: selectedSchool.value,
            subject_id: option.value,
          }),
          context.csrf_token,
          "GET",
        ),
      ),
      instructorsFetcher.fetchData(() =>
        fetchByReactivated(
          reverse("discord_tracker:get_instructors", {
            school_id: selectedSchool.value,
            subject_id: option.value,
          }),
          context.csrf_token,
          "GET",
        ),
      ),
    ]);
  }

  function handleCourseChange(option: CourseOption | null) {
    setSelectedCourse(option);
  }

  function handleInstructorsChange(options: readonly InstructorOption[]) {
    setSelectedInstructors([...options]);
  }

  function handleClose() {
    setInviteUrl("");
    setNotes("");
    setSelectedSchool(null);
    setSelectedSubject(null);
    setSelectedCourse(null);
    setSelectedInstructors([]);
    setShowSchoolSelection(false);
    setGuildInfo(null);
    setIsPublic(false);
    setAvailableSchools([]);
    setIsValidating(false);

    // reset all useFetch states to clear any errors or data from previous sessions
    inviteValidationFetcher.reset();
    submitInviteFetcher.reset();
    subjectsFetcher.reset();
    coursesFetcher.reset();
    instructorsFetcher.reset();

    onHide();
  }

  return (
    <Modal show={show} onHide={handleClose} centered size="lg" backdrop="static">
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
                Optional notes about the server to give extra context
              </Form.Text>
            </Form.Group>

            {inviteValidationFetcher.errorMessages.length > 0 && (
              <Alert variant="danger" className="mb-3">
                {inviteValidationFetcher.errorMessages.map((error, index) => (
                  <div key={index}>{error}</div>
                ))}
              </Alert>
            )}

            {submitInviteFetcher.errorMessages.length > 0 && (
              <Alert variant="danger" className="mb-3">
                {submitInviteFetcher.errorMessages.map((error, index) => (
                  <div key={index}>{error}</div>
                ))}
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
              <strong>Discord Server Validated!</strong> Please associate this server with the
              appropriate academic information.
            </Alert>

            {submitInviteFetcher.data && submitInviteFetcher.errorMessages.length === 0 && (
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
                isClearable
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
                isClearable
                isDisabled={!selectedSubject}
                isLoading={coursesFetcher.isLoading}
                classNamePrefix="react-select"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Instructor(s) (Optional)</Form.Label>
              <Select
                isMulti
                value={selectedInstructors}
                onChange={handleInstructorsChange}
                options={instructorOptions}
                placeholder="Select instructor(s)..."
                isSearchable
                isDisabled={!selectedSubject}
                isLoading={instructorsFetcher.isLoading}
                classNamePrefix="react-select"
              />
              <Form.Text className="text-muted">
                Select one or more instructors who teach this subject (optional)
              </Form.Text>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                id="public-invite-checkbox"
                label="Make this invite publicly visible to all users"
                checked={isPublic}
                onChange={(e) => setIsPublic(e.target.checked)}
              />
              <Form.Text className="text-muted">
                {isManager
                  ? "If unchecked, only registered users can see your invite. Your invites are automatically approved"
                  : "If unchecked, only registered users can see your invite. Note: All of your invites require manager approval before becoming visible to anyone"}
              </Form.Text>
            </Form.Group>

            {submitInviteFetcher.errorMessages.length > 0 && (
              <Alert variant="danger" className="mb-3">
                {submitInviteFetcher.errorMessages.map((error, index) => (
                  <div key={index}>{error}</div>
                ))}
              </Alert>
            )}

            <div className="d-flex justify-content-end">
              <Button
                variant="secondary"
                onClick={() => setShowSchoolSelection(false)}
                className="me-2"
                disabled={submitInviteFetcher.isLoading}
              >
                Back
              </Button>
              <Button
                variant="primary"
                onClick={handleSubmit}
                disabled={
                  !selectedSchool ||
                  submitInviteFetcher.isLoading ||
                  submitInviteFetcher.data !== null
                }
              >
                {submitInviteFetcher.isLoading ? "Submitting..." : "Submit Invite"}
              </Button>
            </div>
          </div>
        )}
      </Modal.Body>
    </Modal>
  );
}
