import React from "react";

import { templates } from "@reactivated";
import { Badge, Button, Card, Col, Container, Row } from "react-bootstrap";

import { faDiscord } from "@fortawesome/free-brands-svg-icons";
import { faExternalLinkAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { Navbar } from "@client/components/discord_tracker/Navbar";
import { Layout } from "@client/layouts/Layout";

export function Template(props: templates.DiscordTrackerUnapprovedInvites) {
  function handleApproveInvite(inviteId: number) {
    // TODO: implement approve functionality
    console.log("Approve invite:", inviteId);
  }

  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function getPrivacyLevelBadge(privacyLevel: string) {
    if (privacyLevel === "public") {
      return (
        <Badge bg="success" className="ms-2">
          Public
        </Badge>
      );
    }
    return (
      <Badge bg="warning" text="dark" className="ms-2">
        Privileged
      </Badge>
    );
  }

  function getUserRoleBadge(roleInfo: { value: string; label: string }) {
    const variant = roleInfo.value === "manager" ? "danger" : "info";
    return (
      <Badge bg={variant} className="ms-1">
        {roleInfo.label}
      </Badge>
    );
  }

  return (
    <Layout title="Unapproved Discord Invites - Discord Tracker" Navbar={Navbar}>
      <Container fluid className="py-4">
        <Row className="justify-content-center">
          <Col lg={10} xl={8}>
            <div className="d-flex align-items-center mb-4">
              <FontAwesomeIcon icon={faDiscord} className="text-primary me-3" size="2x" />
              <div>
                <h1 className="mb-1">Unapproved Discord Invites</h1>
                <p className="text-muted mb-0">
                  Review and approve Discord server invites submitted by trusted users
                </p>
              </div>
            </div>

            {props.unapproved_invites.length === 0 ? (
              <div className="text-center py-5">
                <Card className="border-0">
                  <Card.Body>
                    <FontAwesomeIcon icon={faDiscord} size="3x" className="text-muted mb-3" />
                    <h4>No Pending Invites</h4>
                    <p className="mb-0">All Discord invites have been reviewed and approved.</p>
                  </Card.Body>
                </Card>
              </div>
            ) : (
              <div className="d-grid gap-4">
                {props.unapproved_invites.map((invite) => (
                  <Card key={invite.id} className="border-0 shadow-sm">
                    <Card.Body className="p-4">
                      <Row className="align-items-start">
                        <Col md={8}>
                          <div className="d-flex align-items-start mb-3">
                            {invite.discord_server.icon_url ? (
                              <img
                                src={invite.discord_server.icon_url}
                                alt={`${invite.discord_server.display_name} icon`}
                                className="rounded me-3"
                                style={{ width: "48px", height: "48px", objectFit: "cover" }}
                              />
                            ) : (
                              <div
                                className="bg-light rounded d-flex align-items-center justify-content-center me-3"
                                style={{ width: "48px", height: "48px", flexShrink: 0 }}
                              >
                                <FontAwesomeIcon icon={faDiscord} className="text-muted" />
                              </div>
                            )}
                            <div className="flex-grow-1">
                              <h5 className="mb-1">
                                {invite.discord_server.display_name}
                                {getPrivacyLevelBadge(invite.discord_server.privacy_level)}
                              </h5>
                              <div className="text-muted small mb-2">
                                Submitted by {invite.submitter.display_name}
                                {getUserRoleBadge(invite.submitter.role_info)}
                              </div>
                              <div className="text-muted small">
                                Submitted on {formatDate(invite.datetime_created)}
                              </div>
                            </div>
                          </div>

                          <div className="mb-3">
                            <div className="d-flex align-items-center mb-2">
                              <strong className="me-2">Invite URL:</strong>
                              <code className="bg-light px-2 py-1 rounded text-break flex-grow-1">
                                {invite.invite_url}
                              </code>
                              <a
                                href={invite.invite_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn btn-outline-secondary btn-sm ms-2"
                              >
                                <FontAwesomeIcon icon={faExternalLinkAlt} />
                              </a>
                            </div>
                          </div>

                          {invite.notes_md && (
                            <div className="mb-3">
                              <strong>Notes:</strong>
                              <div className="bg-light rounded p-3 mt-2">
                                <p className="mb-0">{invite.notes_md}</p>
                              </div>
                            </div>
                          )}

                          <div className="d-flex gap-3 text-muted small">
                            <span>
                              <strong>Status:</strong>{" "}
                              <Badge bg={invite.is_valid ? "success" : "danger"}>
                                {invite.is_valid ? "Valid" : "Invalid"}
                              </Badge>
                            </span>
                            {invite.expires_at !== null && invite.expires_at !== "" && (
                              <span>
                                <strong>Expires:</strong> {formatDate(invite.expires_at)}
                              </span>
                            )}
                          </div>
                        </Col>

                        <Col md={4} className="text-md-end">
                          <div className="d-grid gap-2">
                            <Button
                              variant="success"
                              size="lg"
                              onClick={() => handleApproveInvite(invite.id)}
                              disabled={!invite.is_valid}
                            >
                              Approve Invite
                            </Button>
                            <Button variant="outline-danger" size="sm">
                              Reject
                            </Button>
                          </div>
                        </Col>
                      </Row>
                    </Card.Body>
                  </Card>
                ))}
              </div>
            )}
          </Col>
        </Row>
      </Container>
    </Layout>
  );
}
