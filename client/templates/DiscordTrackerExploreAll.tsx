import React, { useContext, useState } from "react";

import { Context, reverse, templates } from "@reactivated";
import { Alert, Button, Col, Container, Row } from "react-bootstrap";

import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import {
  AddInviteModal,
  LoginBanner,
  ServerSearchFilters,
  ServerSectionsDisplay,
  ViewInvitesModal,
} from "@client/components/DiscordTrackerServerListings";
import { Navbar } from "@client/components/discord_tracker/Navbar";
import { Layout } from "@client/layouts/Layout";

type TServer = templates.DiscordTrackerExploreAll["servers"][number];

export function Template(props: templates.DiscordTrackerExploreAll) {
  const context = useContext(Context);
  const [showInvitesModal, setShowInvitesModal] = useState(false);
  const [selectedServer, setSelectedServer] = useState<TServer | null>(null);
  const [showAddInviteModal, setShowAddInviteModal] = useState(false);

  const canUserAddInvites = context.user.discord_user !== null;
  const isAuthenticated = context.user.discord_user !== null;
  const isManager = context.user.discord_user?.role_info.value === "manager";

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

  function handleShowAddInviteModal() {
    setShowAddInviteModal(true);
  }

  function handleCloseAddInviteModal() {
    setShowAddInviteModal(false);
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
    return `${reverse("discord_tracker:explore_all_listings")}?${params.toString()}`;
  }

  return (
    <Layout title="Explore All Discord Servers - Class Cords" Navbar={Navbar}>
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
              {props.is_search_active ? `Search results for class servers` : "All Discord servers"}
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
          </div>
        </div>

        {isAuthenticated && (
          <ServerSearchFilters subjectId={props.subject_id} courseId={props.course_id} />
        )}

        <ServerSectionsDisplay
          servers={props.servers}
          onShowInvites={handleShowInvites}
          showGroupingControls={true}
          initialGrouped={false}
        />

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

        <AddInviteModal show={showAddInviteModal} onHide={handleCloseAddInviteModal} />
      </Container>
    </Layout>
  );
}
