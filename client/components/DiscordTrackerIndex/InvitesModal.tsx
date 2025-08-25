import React, { useEffect, useState } from "react";

import { reverse } from "@reactivated";
import { Alert, Button, Modal, Spinner } from "react-bootstrap";

import { faExternalLinkAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

interface DiscordInvite {
  id: number;
  invite_url: string;
  notes_md: string;
  expires_at: string | null;
  max_uses: number;
  uses_count: number;
  is_valid: boolean;
}

interface Props {
  show: boolean;
  onHide: () => void;
  serverId: number | null;
  serverName: string;
}

export function InvitesModal({ show, onHide, serverId, serverName }: Props) {
  const [invites, setInvites] = useState<DiscordInvite[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (show && serverId !== null) {
      void fetchInvites(serverId);
    }
  }, [show, serverId]);

  const fetchInvites = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(reverse("discord_tracker:server_invites", { server_id: id }));
      if (!response.ok) {
        throw new Error("Failed to fetch invites");
      }
      const data = (await response.json()) as {
        success: boolean;
        invites: DiscordInvite[];
        message: string;
      };
      if (data.success) {
        setInvites(data.invites);
      } else {
        throw new Error(data.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleInviteClick = (inviteUrl: string) => {
    window.open(inviteUrl, "_blank");
  };

  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      <Modal.Header closeButton>
        <Modal.Title>Invites for {serverName}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loading && (
          <div className="text-center py-4">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        )}

        {error !== null && (
          <Alert variant="danger" className="mb-3">
            {error}
          </Alert>
        )}

        {!loading && error === null && invites.length === 0 && (
          <Alert variant="info" className="mb-3">
            No invites available for this server.
          </Alert>
        )}

        {!loading && error === null && invites.length > 0 && (
          <div className="d-grid gap-3">
            {invites.map((invite) => (
              <div key={invite.id} className="border rounded p-3">
                <div className="d-flex justify-content-between align-items-start mb-2">
                  <div className="flex-grow-1">
                    <code className="text-break">{invite.invite_url}</code>
                    {invite.notes_md && (
                      <p className="text-muted small mb-2 mt-1">{invite.notes_md}</p>
                    )}
                  </div>
                  <Button
                    variant="outline-primary"
                    size="sm"
                    onClick={() => handleInviteClick(invite.invite_url)}
                    disabled={!invite.is_valid}
                    className="ms-2 flex-shrink-0"
                  >
                    <FontAwesomeIcon icon={faExternalLinkAlt} className="me-1" />
                    Join
                  </Button>
                </div>

                <div className="d-flex justify-content-between text-muted small">
                  <span>
                    Uses: {invite.uses_count}
                    {invite.max_uses > 0 ? ` / ${invite.max_uses}` : " (unlimited)"}
                  </span>
                  {invite.expires_at !== null && (
                    <span>Expires: {new Date(invite.expires_at).toLocaleDateString()}</span>
                  )}
                  {!invite.is_valid && <span className="text-danger">Invalid</span>}
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
