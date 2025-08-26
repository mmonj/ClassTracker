import React, { useRef, useState } from "react";

import { CSRFToken, Context, reverse, templates } from "@reactivated";
import { Badge, Button, Card, Col, Container, Modal, Row } from "react-bootstrap";

import { faDiscord } from "@fortawesome/free-brands-svg-icons";
import { faCheckCircle, faTimesCircle } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { fetchByReactivated } from "@client/utils";

import { Navbar } from "@client/components/discord_tracker/Navbar";
import { FormFieldset } from "@client/components/forms/FormFieldset";
import { useFetch } from "@client/hooks/useFetch";
import { Layout } from "@client/layouts/Layout";

type SchoolSelectionResponse = {
  success: boolean;
  message: string;
};

export function Template(props: templates.DiscordTrackerProfile) {
  const [showModal, setShowModal] = useState(props.show_school_modal);
  const formRef = useRef<HTMLFormElement>(null);
  const context = React.useContext(Context);

  const schoolSelectionFetcher = useFetch<SchoolSelectionResponse>();

  async function handleSchoolSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!formRef.current) return;

    const formData = new FormData(formRef.current);

    const result = await schoolSelectionFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("discord_tracker:select_school"),
        context.csrf_token,
        "POST",
        formData,
      ),
    );

    if (result.ok) {
      setShowModal(false);
      // reload the page to show updated profile
      window.location.reload();
    }
  }

  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function getRoleBadgeVariant(role: string) {
    switch (role) {
      case "discord_manager":
        return "danger";
      case "trusted":
        return "success";
      default:
        return "secondary";
    }
  }

  return (
    <Layout title="Discord Profile" Navbar={Navbar}>
      {/* school selection modal */}
      <Modal show={showModal === true} onHide={() => {}} backdrop="static" keyboard={false}>
        <Modal.Header>
          <Modal.Title>Select Your School</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Please select your school to continue using the Discord Tracker.</p>

          {schoolSelectionFetcher.errorMessages.length > 0 && (
            <div className="alert alert-danger mb-3" role="alert">
              <strong>Error:</strong>
              <ul className="mb-0 mt-2">
                {schoolSelectionFetcher.errorMessages.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          )}

          <form onSubmit={handleSchoolSubmit} ref={formRef}>
            <CSRFToken />
            <FormFieldset form={props.school_form} />
            <div className="d-flex justify-content-end mt-3">
              <Button type="submit" variant="primary" disabled={schoolSelectionFetcher.isLoading}>
                {schoolSelectionFetcher.isLoading ? "Saving..." : "Save School"}
              </Button>
            </div>
          </form>
        </Modal.Body>
      </Modal>
      <Container className="mt-4 px-0">
        <Row className="justify-content-center">
          <Col md={8} lg={6}>
            <Card>
              <Card.Header className="bg-primary text-white">
                <h4 className="mb-0">Discord Profile</h4>
              </Card.Header>
              <Card.Body>
                <div className="text-center mb-4">
                  {props.discord_user.avatar_url && (
                    <img
                      src={props.discord_user.avatar_url}
                      alt="Discord Avatar"
                      className="rounded-circle mb-3"
                      style={{ width: "80px", height: "80px", border: "3px solid #5865F2" }}
                    />
                  )}
                  <h5 className="mb-1">{props.discord_user.display_name}</h5>
                  <p className="text-muted mb-2">
                    @{props.discord_user.username}
                    {props.discord_user.discriminator && `#${props.discord_user.discriminator}`}
                  </p>

                  <div className="d-flex justify-content-center align-items-center mb-3">
                    <FontAwesomeIcon
                      icon={props.discord_user.is_verified ? faCheckCircle : faTimesCircle}
                      className={
                        props.discord_user.is_verified ? "text-success me-2" : "text-warning me-2"
                      }
                    />
                    <span
                      className={props.discord_user.is_verified ? "text-success" : "text-warning"}
                    >
                      {props.discord_user.is_verified ? "Verified Account" : "Unverified Account"}
                    </span>
                  </div>

                  <Badge
                    bg={getRoleBadgeVariant(props.discord_user.role_info.value)}
                    className="mb-3"
                  >
                    {props.discord_user.role_info.label}
                  </Badge>
                </div>

                {/* profile stats */}
                <Card className="bg-light mb-4">
                  <Card.Body className="py-3">
                    <Row className="text-center">
                      <Col xs={6}>
                        <div className="fw-bold fs-5">{props.discord_user.login_count}</div>
                        <small className="text-muted">Total Logins</small>
                      </Col>
                      <Col xs={6}>
                        <div className="fw-bold fs-5">
                          {new Date(props.discord_user.first_login).toLocaleDateString()}
                        </div>
                        <small className="text-muted">Member Since</small>
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>

                <Row>
                  <Col sm={6}>
                    <strong>Discord ID:</strong>
                  </Col>
                  <Col sm={6}>
                    <code className="text-muted">{props.discord_user.discord_id}</code>
                  </Col>
                </Row>

                <hr />

                <Row>
                  <Col sm={6}>
                    <strong>Email Verified:</strong>
                  </Col>
                  <Col sm={6}>
                    <Badge bg={props.discord_user.is_verified ? "success" : "warning"}>
                      {props.discord_user.is_verified ? "Verified" : "Not Verified"}
                    </Badge>
                  </Col>
                </Row>

                <hr />

                {props.school !== null && (
                  <>
                    <Row>
                      <Col sm={6}>
                        <strong>School:</strong>
                      </Col>
                      <Col sm={6}>{props.school.name}</Col>
                    </Row>
                    <hr />
                  </>
                )}

                <Row>
                  <Col sm={6}>
                    <strong>First Login:</strong>
                  </Col>
                  <Col sm={6}>{formatDate(props.discord_user.first_login)}</Col>
                </Row>

                <hr />

                <Row>
                  <Col sm={6}>
                    <strong>Last Login:</strong>
                  </Col>
                  <Col sm={6}>{formatDate(props.discord_user.last_login)}</Col>
                </Row>

                <hr />

                <Row>
                  <Col sm={6}>
                    <strong>Role:</strong>
                  </Col>
                  <Col sm={6}>
                    <Badge bg={getRoleBadgeVariant(props.discord_user.role_info.value)}>
                      {props.discord_user.role_info.label}
                    </Badge>
                  </Col>
                </Row>

                <hr />

                {/* logout btn */}
                <div className="text-center mt-4">
                  <form action={reverse("account_logout")} method="POST">
                    <CSRFToken />
                    <Button variant="outline-danger" type="submit" className="w-100">
                      <FontAwesomeIcon icon={faDiscord} className="me-2" />
                      Sign Out
                    </Button>
                  </form>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </Layout>
  );
}
