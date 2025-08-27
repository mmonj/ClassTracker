import React, { useContext, useEffect } from "react";

import { Context, interfaces, reverse, templates } from "@reactivated";
import { Alert, Badge, Button, Card, Modal, Spinner } from "react-bootstrap";

import { faDiscord } from "@fortawesome/free-brands-svg-icons";
import { faExternalLinkAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { fetchByReactivated } from "@client/utils";

import { useFetch } from "@client/hooks/useFetch";

import { DiscordServerInfo } from "./DiscordServerInfo";

interface Props {
  show: boolean;
  onHide: () => void;
  server: templates.DiscordTrackerIndex["public_servers"][number] | null;
}

const ICON_VERTICAL_OFFSET = 45;

export function ViewInvitesModal({ show, onHide, server }: Props) {
  const context = useContext(Context);
  const invitesFetcher = useFetch<interfaces.ServerInvitesResponse>();

  useEffect(() => {
    if (show && server !== null) {
      void fetchInvites(server.id);
    }
  }, [show, server]);

  async function fetchInvites(id: number) {
    await invitesFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("discord_tracker:server_invites", { server_id: id }),
        context.csrf_token,
        "GET",
      ),
    );
  }

  function handleInviteClick(
    event: React.MouseEvent<HTMLAnchorElement | HTMLButtonElement>,
    inviteId: number,
  ) {
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
    <Modal show={show} onHide={onHide} size="lg" centered backdrop="static">
      {/* floating server icon right above modal header */}
      {server && (
        <div
          className="position-absolute start-50 translate-middle-x bg-white rounded-circle shadow-lg border"
          style={{
            top: `-${ICON_VERTICAL_OFFSET}px`,
            zIndex: 1060,
            width: `${ICON_VERTICAL_OFFSET * 2}px`,
            height: `${ICON_VERTICAL_OFFSET * 2}px`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "4px",
          }}
        >
          {server.icon_url ? (
            <img
              src={server.icon_url}
              alt={`${server.display_name} icon`}
              className="rounded-circle"
              style={{
                width: `${ICON_VERTICAL_OFFSET * 2 - 10}px`,
                height: `${ICON_VERTICAL_OFFSET * 2 - 10}px`,
                objectFit: "cover",
              }}
            />
          ) : (
            <FontAwesomeIcon icon={faDiscord} className="text-muted" size="2x" />
          )}
        </div>
      )}
      <Modal.Header className="pt-5">
        <Modal.Title className="w-100 text-center">
          {server ? (
            <div className="mt-2">
              <h4 className="mb-1">{server.display_name}</h4>
              <div className="d-flex justify-content-center gap-2">
                <span
                  className={`badge bg-${server.privacy_level === "public" ? "success" : "warning"}`}
                >
                  {server.privacy_level === "public" ? "Public" : "Privileged"}
                </span>
                {server.is_general_server && <span className="badge bg-info">General Server</span>}
              </div>
            </div>
          ) : (
            <div className="mt-2">
              <h4 className="mb-1">Discord Server Invites</h4>
            </div>
          )}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {server && server.description && (
          <div className="mb-4 text-center">
            <p className="text-muted mb-0">{server.description}</p>
          </div>
        )}

        {/* relevant academic info of this server */}
        {server && <DiscordServerInfo server={server} className="mb-4 border-0 bg-light" />}
        {invitesFetcher.isLoading && (
          <div className="text-center py-4">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        )}

        {invitesFetcher.errorMessages.length > 0 && (
          <Alert variant="danger" className="mb-3">
            <ul className="mb-0" style={{ listStyleType: "disclosure-closed" }}>
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

        {/* invites list */}
        {invitesFetcher.data !== null && invitesFetcher.data.invites.length > 0 && (
          <div className="d-grid gap-2">
            {invitesFetcher.data.invites.map((invite) => {
              const bgClass = !invite.is_valid ? "bg-light" : "";
              const borderLeftStyles = invite.is_valid ? "4px solid #0d6efd" : "4px solid #dc3545";

              return (
                <Card
                  key={invite.id}
                  className={`border-0 shadow-sm ${bgClass}`}
                  style={{
                    borderLeft: borderLeftStyles,
                  }}
                >
                  <Card.Body className="p-3">
                    <div className="d-flex justify-content-between align-items-start mb-3">
                      <div className="flex-grow-1">
                        <div className="d-flex align-items-center mb-2">
                          <code className="bg-light px-2 py-1 rounded text-break me-2 flex-grow-1">
                            {invite.invite_url}
                          </code>
                          {!invite.is_valid && (
                            <Badge bg="danger" className="ms-2">
                              Invalid
                            </Badge>
                          )}
                        </div>
                        {invite.notes_md && (
                          <div className="bg-light rounded p-2 mt-2">
                            <small className="text-muted mb-0">{invite.notes_md}</small>
                          </div>
                        )}
                      </div>
                      {invite.is_valid ? (
                        <Button
                          as="a"
                          href={invite.invite_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          variant="primary"
                          size="sm"
                          className="ms-3 flex-shrink-0 text-decoration-none"
                          onClick={(e) => handleInviteClick(e, invite.id)}
                        >
                          <FontAwesomeIcon icon={faExternalLinkAlt} className="me-1" />
                          Join
                        </Button>
                      ) : (
                        <Button
                          variant="outline-secondary"
                          size="sm"
                          className="ms-3 flex-shrink-0"
                          disabled
                        >
                          <FontAwesomeIcon icon={faExternalLinkAlt} className="me-1" />
                          Invalid
                        </Button>
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
                  </Card.Body>
                </Card>
              );
            })}
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
