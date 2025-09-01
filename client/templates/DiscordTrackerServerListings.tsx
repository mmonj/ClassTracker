import React, { useContext, useMemo, useState } from "react";

import { Context, reverse, templates } from "@reactivated";
import { Alert, Button, Col, Collapse, Container, Row } from "react-bootstrap";

import {
  faChevronDown,
  faChevronUp,
  faEye,
  faEyeSlash,
  faLayerGroup,
  faList,
  faPlus,
  faSearch,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import {
  AddInviteModal,
  DiscordServerCard,
  LoginBanner,
  ServerSearchFilters,
  ViewInvitesModal,
} from "@client/components/DiscordTrackerServerListings";
import { Navbar } from "@client/components/discord_tracker/Navbar";
import { Layout } from "@client/layouts/Layout";

type TServer = templates.DiscordTrackerServerListings["servers"][number];

export function Template(props: templates.DiscordTrackerServerListings) {
  const context = useContext(Context);
  const [showInvitesModal, setShowInvitesModal] = useState(false);
  const [selectedServer, setSelectedServer] = useState<TServer | null>(null);
  const [publicSectionOpen, setPublicSectionOpen] = useState(true);
  const [privateSectionOpen, setPrivateSectionOpen] = useState(true);
  const [showAddInviteModal, setShowAddInviteModal] = useState(false);

  const isBasePage = !props.is_search_active && !props.pagination;
  const [isGrouped, setIsGrouped] = useState(isBasePage); // default to grouped on base page, ungrouped on pagination

  const canUserAddInvites = context.user.discord_user !== null;
  const isAuthenticated = context.user.discord_user !== null;
  const isManager = context.user.discord_user?.role_info.value === "manager";

  // group servers by privacy level and 'required' status
  const { publicServers, privateServers, requiredServers } = useMemo(() => {
    const required: TServer[] = [];
    const publicNormal: TServer[] = [];
    const privateNormal: TServer[] = [];

    props.servers.forEach((server) => {
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
  }, [props.servers]);

  function handleShowInvites(serverId: number) {
    const server = props.servers.find((s) => s.id === serverId);
    if (server) {
      setSelectedServer(server);
      setShowInvitesModal(true);
    }
  }

  function handleCloseInvitesModal() {
    setShowInvitesModal(false);
    setSelectedServer(null);
  }

  function handleToggleCollapseAll() {
    const shouldCollapseAll = publicSectionOpen || privateSectionOpen;
    setPublicSectionOpen(!shouldCollapseAll);
    setPrivateSectionOpen(!shouldCollapseAll);
  }

  function handleShowAddInviteModal() {
    setShowAddInviteModal(true);
  }

  function handleCloseAddInviteModal() {
    setShowAddInviteModal(false);
  }

  function handleToggleGrouping() {
    setIsGrouped(!isGrouped);
  }

  function buildPageUrl(page: number) {
    const params = new URLSearchParams();
    params.set("page", page.toString());
    if (props.subject_id !== null) {
      params.set("subject_id", props.subject_id.toString());
    }
    if (props.course_id !== null) {
      params.set("course_id", props.course_id.toString());
    }
    return `${reverse("discord_tracker:listings")}?${params.toString()}`;
  }

  return (
    <Layout title="Class Cords" Navbar={Navbar}>
      <Container className="py-4">
        {!context.user.is_authenticated && <LoginBanner />}

        {isManager && props.pending_invites_count > 0 && (
          <Alert variant="warning" className="mb-4">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <strong>{props.pending_invites_count}</strong> pending invite submission(s) awaiting
                approval
              </div>
              <Button
                variant="outline-secondary"
                size="sm"
                href={reverse("discord_tracker:unapproved_invites")}
              >
                Review Invites
              </Button>
            </div>
          </Alert>
        )}

        <div className="text-center mb-4">
          <div className="mb-3">
            <h1 className="mb-1">Discord Servers</h1>
            <p className="text-muted mb-0">
              {props.is_search_active
                ? `Search results for class servers`
                : isBasePage
                  ? "Recently added Discord servers for your classes"
                  : "All Discord servers"}
            </p>
          </div>

          <div className="d-flex flex-column flex-sm-row justify-content-center gap-2">
            {/* add new discord invite */}
            {canUserAddInvites && (
              <Button
                variant="success"
                size="sm"
                onClick={handleShowAddInviteModal}
                className="d-flex align-items-center justify-content-center"
              >
                <FontAwesomeIcon icon={faPlus} className="me-2" />
                Add Discord Invite
              </Button>
            )}

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
              !props.is_search_active &&
              !props.pagination &&
              (publicServers.length > 0 || privateServers.length > 0) && (
                <Button
                  variant="outline-secondary"
                  size="sm"
                  onClick={handleToggleCollapseAll}
                  className="d-flex align-items-center justify-content-center"
                >
                  <FontAwesomeIcon
                    icon={publicSectionOpen || privateSectionOpen ? faEyeSlash : faEye}
                    className="me-2"
                  />
                  {publicSectionOpen || privateSectionOpen ? "Collapse All" : "Expand All"}
                </Button>
              )}

            {/* 'explore all' button */}
            {isBasePage && (
              <Button
                href={buildPageUrl(1)}
                variant="outline-primary"
                size="sm"
                className="d-flex align-items-center justify-content-center"
              >
                <FontAwesomeIcon icon={faSearch} className="me-2" />
                Explore All Class Servers
              </Button>
            )}
          </div>
        </div>

        {isAuthenticated && props.pagination && (
          <ServerSearchFilters subjectId={props.subject_id} courseId={props.course_id} />
        )}

        {/* featured servers section */}
        {isGrouped && requiredServers.length > 0 && (
          <div className="mb-5">
            <div className="d-flex align-items-center mb-3">
              <h3 className="mb-0 text-success">Featured Servers</h3>
              <span className="badge bg-success ms-2">{requiredServers.length}</span>
            </div>
            <Row>
              {requiredServers.map((server) => (
                <DiscordServerCard
                  key={server.id}
                  server={server}
                  onShowInvites={handleShowInvites}
                />
              ))}
            </Row>
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
                      onShowInvites={handleShowInvites}
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
                      onShowInvites={handleShowInvites}
                    />
                  ))}
                </Row>
              </div>
            </Collapse>
          </div>
        )}

        {/* Ungrouped/List View */}
        {!isGrouped && (
          <div className="mb-5">
            <Row>
              {props.servers.map((server) => (
                <DiscordServerCard
                  key={server.id}
                  server={server}
                  onShowInvites={handleShowInvites}
                />
              ))}
            </Row>
          </div>
        )}

        {/* no servers msg */}
        {props.servers.length === 0 && (
          <Alert variant="info" className="text-center">
            <h4>No Discord servers found</h4>
            <p className="mb-0">
              {props.is_search_active
                ? "Try adjusting your search criteria."
                : "Check back later for new servers or contact an administrator."}
            </p>
          </Alert>
        )}

        {/* pagination */}
        {props.pagination && props.pagination.total_pages > 1 && (
          <nav aria-label="Discord servers pagination">
            <Row className="justify-content-between align-items-center mt-4">
              <Col md="auto">
                <span className="text-muted">
                  Page {props.pagination.current_page} of {props.pagination.total_pages}
                </span>
              </Col>
              <Col md="auto">
                <div className="btn-group" role="group">
                  {props.pagination.has_previous && (
                    <>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        href={buildPageUrl(1)}
                        disabled={props.pagination.current_page === 1}
                      >
                        First
                      </Button>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        href={buildPageUrl(props.pagination.previous_page_number)}
                      >
                        Previous
                      </Button>
                    </>
                  )}

                  <Button variant="primary" size="sm" disabled>
                    {props.pagination.current_page}
                  </Button>

                  {props.pagination.has_next && (
                    <>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        href={buildPageUrl(props.pagination.next_page_number)}
                      >
                        Next
                      </Button>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        href={buildPageUrl(props.pagination.total_pages)}
                        disabled={props.pagination.current_page === props.pagination.total_pages}
                      >
                        Last
                      </Button>
                    </>
                  )}
                </div>
              </Col>
            </Row>
          </nav>
        )}

        <ViewInvitesModal
          show={showInvitesModal}
          onHide={handleCloseInvitesModal}
          server={selectedServer}
        />

        {/* Add Invite Modal */}
        <AddInviteModal show={showAddInviteModal} onHide={handleCloseAddInviteModal} />
      </Container>
    </Layout>
  );
}
