import React, { useContext, useEffect } from "react";

import { Context, interfaces, reverse } from "@reactivated";
import { Alert, Button, Modal, Spinner } from "react-bootstrap";

import { faExternalLinkAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { fetchByReactivated } from "@client/utils";

import { useFetch } from "@client/hooks/useFetch";

interface Props {
  show: boolean;
  onHide: () => void;
  serverId: number | null;
  serverName: string;
}

export function InvitesModal({ show, onHide, serverId, serverName }: Props) {
  const context = useContext(Context);
  const invitesFetcher = useFetch<interfaces.ServerInvitesResponse>();

  useEffect(() => {
    if (show && serverId !== null) {
      void fetchInvites(serverId);
    }
  }, [show, serverId]);

  async function fetchInvites(id: number) {
    await invitesFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("discord_tracker:server_invites", { server_id: id }),
        context.csrf_token,
        "GET",
      ),
    );
  }

  function handleInviteClick(event: React.MouseEvent<HTMLAnchorElement>, inviteId: number) {
    void fetchByReactivated(
      reverse("discord_tracker:track_invite_usage", { invite_id: inviteId }),
      context.csrf_token,
      "PUT",
    ).catch((error) => {
      console.warn("Failed to track invite usage:", error);
    });

    // anchor link navigation happens once function exits
  }

  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      <Modal.Header closeButton>
        <Modal.Title>Invites for {serverName}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {invitesFetcher.isLoading && (
          <div className="text-center py-4">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        )}

        {invitesFetcher.errorMessages.length > 0 && (
          <Alert variant="danger" className="mb-3">
            <ul className="mb-0">
              {invitesFetcher.errorMessages.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </Alert>
        )}

        {invitesFetcher.data?.invites.length === 0 && (
          <Alert variant="info" className="mb-3">
            No invites available for this server.
          </Alert>
        )}

        {invitesFetcher.data !== null && invitesFetcher.data.invites.length > 0 && (
          <div className="d-grid gap-3">
            {invitesFetcher.data.invites.map((invite) => (
              <div
                key={invite.id}
                className={`card border-0 shadow-sm ${!invite.is_valid ? "bg-light" : ""}`}
                style={{ borderLeft: invite.is_valid ? "4px solid #0d6efd" : "4px solid #dc3545" }}
              >
                <div className="card-body p-3">
                  <div className="d-flex justify-content-between align-items-start mb-3">
                    <div className="flex-grow-1">
                      <div className="d-flex align-items-center mb-2">
                        <code className="bg-light px-2 py-1 rounded text-break me-2 flex-grow-1">
                          {invite.invite_url}
                        </code>
                        {!invite.is_valid && <span className="badge bg-danger ms-2">Invalid</span>}
                      </div>
                      {invite.notes_md && (
                        <div className="bg-light rounded p-2 mt-2">
                          <small className="text-muted mb-0">{invite.notes_md}</small>
                        </div>
                      )}
                    </div>
                    {invite.is_valid ? (
                      <a
                        href={invite.invite_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-primary btn-sm ms-3 flex-shrink-0 text-decoration-none"
                        onClick={(e) => handleInviteClick(e, invite.id)}
                      >
                        <FontAwesomeIcon icon={faExternalLinkAlt} className="me-1" />
                        Join
                      </a>
                    ) : (
                      <span className="btn btn-outline-secondary btn-sm ms-3 flex-shrink-0 disabled">
                        <FontAwesomeIcon icon={faExternalLinkAlt} className="me-1" />
                        Invalid
                      </span>
                    )}
                  </div>

                  <div className="d-flex justify-content-between align-items-center">
                    <div className="d-flex gap-3 text-muted small">
                      <span className="d-flex align-items-center">
                        <i className="bi bi-people me-1"></i>
                        Uses: <span className="fw-bold ms-1">{invite.uses_count}</span>
                      </span>

                      {invite.is_unlimited && (
                        <span className="text-success ms-1">Non-Expiring Invite</span>
                      )}

                      {invite.expires_at !== null && (
                        <span className="d-flex align-items-center">
                          <i className="bi bi-clock me-1"></i>
                          Expires:{" "}
                          <span className="fw-bold ms-1">
                            {new Date(invite.expires_at).toLocaleDateString()}
                          </span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
