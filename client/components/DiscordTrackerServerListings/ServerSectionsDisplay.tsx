import React, { useMemo, useState } from "react";

import { templates } from "@reactivated";
import { Alert, Button, Collapse, Row } from "react-bootstrap";

import {
  faChevronDown,
  faChevronUp,
  faEye,
  faEyeSlash,
  faLayerGroup,
  faList,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import { DiscordServerCard } from "./DiscordServerCard";

type TServer = templates.DiscordTrackerExploreAll["servers"][number];

interface Props {
  servers: TServer[];
  onShowInvites: (serverId: number) => void;
  showGroupingControls?: boolean;
  initialGrouped?: boolean;
}

export function ServerSectionsDisplay({
  servers,
  onShowInvites,
  showGroupingControls = true,
  initialGrouped = true,
}: Props) {
  const [requiredSectionOpen, setRequiredSectionOpen] = useState(true);
  const [publicSectionOpen, setPublicSectionOpen] = useState(true);
  const [privateSectionOpen, setPrivateSectionOpen] = useState(true);
  const [isGrouped, setIsGrouped] = useState(initialGrouped);

  // group servers by privacy level and 'required' status
  const { publicServers, privateServers, requiredServers } = useMemo(() => {
    const required: TServer[] = [];
    const publicNormal: TServer[] = [];
    const privateNormal: TServer[] = [];

    servers.forEach((server) => {
      if (server.is_required_for_trust) {
        required.push(server);
      } else if (server.privacy_level_info.value === "public") {
        publicNormal.push(server);
      } else {
        privateNormal.push(server);
      }
    });

    return {
      requiredServers: required,
      publicServers: publicNormal,
      privateServers: privateNormal,
    };
  }, [servers]);

  function handleToggleCollapseAll() {
    const shouldCollapseAll = requiredSectionOpen || publicSectionOpen || privateSectionOpen;
    setRequiredSectionOpen(!shouldCollapseAll);
    setPublicSectionOpen(!shouldCollapseAll);
    setPrivateSectionOpen(!shouldCollapseAll);
  }

  function handleToggleGrouping() {
    setIsGrouped(!isGrouped);
  }

  if (servers.length === 0) {
    return (
      <Alert variant="info" className="text-center">
        <h4>No Discord servers found</h4>
        <p className="mb-0">Check back later for new servers or contact an administrator.</p>
      </Alert>
    );
  }

  return (
    <>
      {/* Grouping Controls */}
      {showGroupingControls && (
        <div className="d-flex flex-column flex-sm-row justify-content-center gap-2 mb-4">
          {/* grouping toggle button */}
          <Button
            variant={isGrouped ? "primary" : "outline-primary"}
            size="sm"
            onClick={handleToggleGrouping}
            className="d-flex align-items-center justify-content-center"
          >
            <FontAwesomeIcon icon={isGrouped ? faLayerGroup : faList} className="me-2" />
            {isGrouped ? "Grouped" : "List View"}
          </Button>

          {/* 'collapse/uncollapse all' */}
          {isGrouped &&
            (requiredServers.length > 0 ||
              publicServers.length > 0 ||
              privateServers.length > 0) && (
              <Button
                variant="outline-secondary"
                size="sm"
                onClick={handleToggleCollapseAll}
                className="d-flex align-items-center justify-content-center"
              >
                <FontAwesomeIcon
                  icon={
                    requiredSectionOpen || publicSectionOpen || privateSectionOpen
                      ? faEyeSlash
                      : faEye
                  }
                  className="me-2"
                />
                {requiredSectionOpen || publicSectionOpen || privateSectionOpen
                  ? "Collapse All"
                  : "Expand All"}
              </Button>
            )}
        </div>
      )}

      {/* featured servers section */}
      {isGrouped && requiredServers.length > 0 && (
        <div className="mb-5">
          <div
            className={classNames(
              "d-flex align-items-center justify-content-between mb-3 p-3 rounded",
              "bg-success bg-opacity-10 border border-success border-opacity-25",
            )}
            onClick={() => setRequiredSectionOpen(!requiredSectionOpen)}
            style={{ cursor: "pointer" }}
          >
            <div className="d-flex align-items-center">
              <h3 className="mb-0 text-success">Featured Servers</h3>
              <span className="badge bg-success ms-2">{requiredServers.length}</span>
            </div>
            <FontAwesomeIcon
              icon={requiredSectionOpen ? faChevronUp : faChevronDown}
              className="text-success"
            />
          </div>
          <Collapse in={requiredSectionOpen}>
            <div>
              <Row>
                {requiredServers.map((server) => (
                  <DiscordServerCard
                    key={server.id}
                    server={server}
                    onShowInvites={onShowInvites}
                  />
                ))}
              </Row>
            </div>
          </Collapse>
        </div>
      )}

      {/* public servers */}
      {isGrouped && publicServers.length > 0 && (
        <div className="mb-5">
          <div
            className={classNames(
              "d-flex align-items-center justify-content-between mb-3 p-3 rounded",
              "bg-primary bg-opacity-10 border border-primary border-opacity-25",
            )}
            onClick={() => setPublicSectionOpen(!publicSectionOpen)}
            style={{ cursor: "pointer" }}
          >
            <div className="d-flex align-items-center">
              <h3 className="mb-0 text-primary">Public Servers</h3>
              <span className="badge bg-primary ms-2 text-dark">{publicServers.length}</span>
            </div>
            <FontAwesomeIcon
              icon={publicSectionOpen ? faChevronUp : faChevronDown}
              className="text-primary"
            />
          </div>
          <Collapse in={publicSectionOpen}>
            <div>
              <Row>
                {publicServers.map((server) => (
                  <DiscordServerCard
                    key={server.id}
                    server={server}
                    onShowInvites={onShowInvites}
                  />
                ))}
              </Row>
            </div>
          </Collapse>
        </div>
      )}

      {/* private servers secton */}
      {isGrouped && privateServers.length > 0 && (
        <div className="mb-5">
          <div
            className={classNames(
              "d-flex align-items-center justify-content-between mb-3 p-3 rounded",
              "bg-warning bg-opacity-10 border border-warning border-opacity-25",
            )}
            onClick={() => setPrivateSectionOpen(!privateSectionOpen)}
            style={{ cursor: "pointer" }}
          >
            <div className="d-flex align-items-center">
              <h3 className="mb-0 text-warning">Private Servers</h3>
              <span className="badge bg-warning text-light ms-2">{privateServers.length}</span>
            </div>
            <FontAwesomeIcon
              icon={privateSectionOpen ? faChevronUp : faChevronDown}
              className="text-warning"
            />
          </div>
          <Collapse in={privateSectionOpen}>
            <div>
              <Row>
                {privateServers.map((server) => (
                  <DiscordServerCard
                    key={server.id}
                    server={server}
                    onShowInvites={onShowInvites}
                  />
                ))}
              </Row>
            </div>
          </Collapse>
        </div>
      )}

      {/* ungrouped/list view */}
      {!isGrouped && (
        <div className="mb-5">
          <Row>
            {servers.map((server) => (
              <DiscordServerCard key={server.id} server={server} onShowInvites={onShowInvites} />
            ))}
          </Row>
        </div>
      )}
    </>
  );
}
