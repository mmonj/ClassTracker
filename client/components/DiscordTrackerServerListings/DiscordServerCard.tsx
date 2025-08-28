import React from "react";

import { templates } from "@reactivated";
import { Button, Card, Col } from "react-bootstrap";

import { faLock, faUsers } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { DiscordServerInfo } from "./DiscordServerInfo";

interface Props {
  server: templates.DiscordTrackerServerListings["public_servers"][number];
  onShowInvites: (serverId: number) => void;
}

export function DiscordServerCard({ server, onShowInvites }: Props) {
  const isPrivileged = server.privacy_level_info.value === "privileged";

  return (
    <Col xs={12} md={6} lg={4} className="mb-4">
      <Card className="h-100 shadow-sm">
        <Card.Body className="d-flex flex-column">
          <div className="d-flex align-items-center mb-1">
            {server.icon_url ? (
              <img
                src={server.icon_url}
                alt={`${server.display_name} icon`}
                className="rounded-circle me-3"
                width="40"
                height="40"
                onError={(e) => {
                  // fallback if image fails to load
                  const target = e.target as HTMLImageElement;
                  target.style.display = "none";
                  target.nextElementSibling?.classList.remove("d-none");
                }}
              />
            ) : null}
            <div
              className={`rounded-circle bg-secondary d-flex align-items-center justify-content-center me-3 text-white fw-bold ${
                server.icon_url ? "d-none" : ""
              }`}
              style={{
                width: 40,
                height: 40,
                minWidth: 40,
                minHeight: 40,
              }}
            >
              {server.display_name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-grow-1">
              <h5 className="card-title mb-1">{server.display_name}</h5>
              <div className="d-flex align-items-center">
                <FontAwesomeIcon
                  icon={isPrivileged ? faLock : faUsers}
                  className={`me-1 ${isPrivileged ? "text-warning" : "text-primary"}`}
                  size="sm"
                />
                <small className={isPrivileged ? "text-warning" : "text-muted"}>
                  {isPrivileged ? "Private" : "Public"}
                </small>
              </div>
            </div>
          </div>

          {server.description && <p className="text-muted small mb-3">{server.description}</p>}

          {/* relevant academic info */}
          <DiscordServerInfo server={server} className="mb-0 border-0" />

          <div className="mt-auto">
            <Button
              variant={isPrivileged ? "outline-warning" : "outline-primary"}
              className="w-100"
              onClick={() => onShowInvites(server.id)}
            >
              View Info
            </Button>
          </div>
        </Card.Body>
      </Card>
    </Col>
  );
}
