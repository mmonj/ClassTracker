import React, { useContext, useState } from "react";

import { Context, interfaces, reverse, templates } from "@reactivated";
import { Alert, Badge, Card, Col, Row } from "react-bootstrap";

import { faDiscord } from "@fortawesome/free-brands-svg-icons";
import { faExternalLinkAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { motion } from "framer-motion";

import { fetchByReactivated, formatDateTypical } from "@client/utils";

import { ButtonWithSpinner } from "@client/components/ButtonWithSpinner";
import { useFetch } from "@client/hooks/useFetch";

interface Props {
  invite: templates.DiscordTrackerUnapprovedInvites["unapproved_invites"][number];
  onApproveSubmit: (inviteId: number) => void;
  onRejectSubmit: (inviteId: number) => void;
}

export function UnapprovedInviteCard({
  invite,
  onApproveSubmit: onApproved,
  onRejectSubmit: onRejected,
}: Props) {
  const context = useContext(Context);
  const approveInviteFetcher = useFetch<interfaces.BlankResponse>();
  const rejectInviteFetcher = useFetch<interfaces.BlankResponse>();
  const [isApproved, setIsApproved] = useState(false);
  const [isRejected, setIsRejected] = useState(false);

  async function handleApproveInvite() {
    const result = await approveInviteFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("discord_tracker:approve_invite", { invite_id: invite.id }),
        context.csrf_token,
        "POST",
      ),
    );

    if (!result.ok) {
      console.warn("Failed to approve invite:", result.errors);
      return;
    }

    // starts the card shrink animation
    setIsApproved(true);

    // let animation to complete before notifying parent
    setTimeout(() => {
      onApproved(invite.id);
    }, 300);
  }

  async function handleRejectInvite() {
    const result = await rejectInviteFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("discord_tracker:reject_invite", { invite_id: invite.id }),
        context.csrf_token,
        "POST",
      ),
    );

    if (!result.ok) {
      console.warn("Failed to reject invite:", result.errors);
      return;
    }

    // starts the card shrink animation
    setIsRejected(true);

    setTimeout(() => {
      onRejected(invite.id);
    }, 300);
  }

  function getPrivacyLevelBadge(
    inviteInfo: templates.DiscordTrackerUnapprovedInvites["unapproved_invites"][number]["discord_server"]["privacy_level_info"],
  ) {
    const badgeColor = inviteInfo.value === "public" ? "success" : "warning";
    return (
      <Badge bg={badgeColor} className="ms-2">
        {inviteInfo.label}
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
    <motion.div
      animate={
        isApproved || isRejected
          ? {
              scale: 0,
              opacity: 0,
              height: 0,
              marginBottom: 0,
            }
          : {
              scale: 1,
              opacity: 1,
              height: "auto",
              marginBottom: "1rem",
            }
      }
      transition={{
        duration: 0.3,
        ease: "easeInOut",
      }}
      style={{ overflow: "hidden" }}
    >
      <Card className="border-0 shadow-sm">
        <Card.Body className="p-4">
          {approveInviteFetcher.errorMessages.length > 0 && (
            <Alert variant="danger" className="mb-3">
              {approveInviteFetcher.errorMessages.map((error, index) => (
                <div key={index}>{error}</div>
              ))}
            </Alert>
          )}
          {rejectInviteFetcher.errorMessages.length > 0 && (
            <Alert variant="danger" className="mb-3">
              {rejectInviteFetcher.errorMessages.map((error, index) => (
                <div key={index}>{error}</div>
              ))}
            </Alert>
          )}

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
                    {getPrivacyLevelBadge(invite.discord_server.privacy_level_info)}
                  </h5>
                  <div className="text-muted small mb-2">
                    Submitted by {invite.submitter.display_name}
                    {getUserRoleBadge(invite.submitter.role_info)}
                  </div>
                  <div className="text-muted small">
                    Submitted on {formatDateTypical(invite.datetime_created)}
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
                    <pre className="mb-0" style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>
                      {invite.notes_md}
                    </pre>
                  </div>
                </div>
              )}

              <div className="d-flex gap-3 text-muted small mb-3 mb-md-0">
                <span>
                  <strong>Invite Status:</strong>{" "}
                  <Badge bg={invite.is_valid ? "success" : "danger"}>
                    {invite.is_valid ? "Valid" : "Invalid"}
                  </Badge>
                </span>
                {invite.expires_at !== null && invite.expires_at !== "" && (
                  <span>
                    <strong>Expires:</strong> {formatDateTypical(invite.expires_at)}
                  </span>
                )}
              </div>
            </Col>

            <Col md={4} className="text-md-end">
              <div className="d-grid gap-2">
                <ButtonWithSpinner
                  className="btn btn-success"
                  onClick={handleApproveInvite}
                  disabled={!invite.is_valid || approveInviteFetcher.data !== null}
                  isLoadingState={approveInviteFetcher.isLoading}
                  spinnerSize="sm"
                >
                  Approve Invite
                </ButtonWithSpinner>
                <ButtonWithSpinner
                  className="btn btn-outline-danger"
                  onClick={handleRejectInvite}
                  disabled={!invite.is_valid || rejectInviteFetcher.data !== null}
                  isLoadingState={rejectInviteFetcher.isLoading}
                  spinnerSize="sm"
                >
                  Reject
                </ButtonWithSpinner>
              </div>
            </Col>
          </Row>
        </Card.Body>
      </Card>
    </motion.div>
  );
}
