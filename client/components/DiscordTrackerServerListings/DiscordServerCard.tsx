import React from "react";

import { templates } from "@reactivated";
import { Button, Card, Col } from "react-bootstrap";

import { faLock, faLockOpen, faShieldAlt, faUsers } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import { DiscordServerInfo } from "./DiscordServerInfo";

interface Props {
  server: templates.DiscordTrackerServerListings["servers"][number];
  onShowInvites: (serverId: number) => void;
}

export function DiscordServerCard({ server, onShowInvites }: Props) {
  const isPrivateServer = server.privacy_level_info.value === "private";

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
              className={classNames(
                "rounded-circle bg-secondary d-flex align-items-center justify-content-center me-3 text-white fw-bold",
                { "d-none": server.icon_url },
              )}
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
              <div className="d-flex align-items-center gap-2 mb-1">
                <h5 className="card-title mb-0">{server.display_name}</h5>
                {server.is_required_for_trust && (
                  <span className="badge bg-success d-inline-flex align-items-center">
                    <FontAwesomeIcon icon={faShieldAlt} className="me-1" size="xs" />
                    Featured
                  </span>
                )}
              </div>
              <div className="d-flex align-items-center gap-3">
                <div className="d-flex align-items-center">
                  <FontAwesomeIcon
                    icon={isPrivateServer ? faLock : faLockOpen}
                    className={classNames("me-1", {
                      "text-warning": isPrivateServer,
                      "text-success": !isPrivateServer,
                    })}
                    size="sm"
                  />
                  <small className={isPrivateServer ? "text-warning" : "text-muted"}>
                    {isPrivateServer ? "Private" : "Public"}
                  </small>
                </div>
                {server.member_count > 0 && (
                  <div className="d-flex align-items-center">
                    <FontAwesomeIcon icon={faUsers} className="me-1 text-muted" size="sm" />
                    <small className="text-muted">{server.member_count.toLocaleString()}</small>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* relevant academic info */}
          <DiscordServerInfo
            server={server}
            truncate_description={true}
            className="mb-0 border-0"
          />

          <div className="mt-auto">
            <Button
              variant={isPrivateServer ? "outline-warning" : "outline-primary"}
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
