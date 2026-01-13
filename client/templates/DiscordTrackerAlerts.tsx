import React, { useContext, useState } from "react";

import { Alert as BootstrapAlert, Card, Container, Modal } from "react-bootstrap";
import Markdown from "react-markdown";

import { Context, interfaces, reverse, templates } from "@reactivated";

import { Navbar } from "@client/components/discord_tracker/Navbar";
import { useFetch } from "@client/hooks/useFetch";
import { Layout } from "@client/layouts/Layout";
import { fetchByReactivated, formatDateTypical } from "@client/utils";

import classNames from "classnames";

export function Template(props: templates.DiscordTrackerAlerts) {
  const [showModal, setShowModal] = useState(false);
  const context = useContext(Context);

  const alertFetcher = useFetch<interfaces.GetAlertDetailsResponse>();

  async function handleAlertClick(userAlertId: number) {
    setShowModal(true);

    const result = await alertFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("discord_tracker:get_alert_details", { user_alert_id: userAlertId }),
        context.csrf_token,
        "GET",
      ),
    );

    const currentAlert = props.user_alerts.find((userAlert) => userAlert.alert.id === userAlertId);
    if (!result.ok || currentAlert === undefined || currentAlert.is_read) return;

    // mark alert read if not already read
    await fetchByReactivated(
      reverse("discord_tracker:mark_alert_as_read", { user_alert_id: userAlertId }),
      context.csrf_token,
      "PUT",
    );
  }

  return (
    <Layout title="Alerts" description="View your notifications and alerts" Navbar={Navbar}>
      <Container className="py-5">
        <div className="text-center mb-5">
          <h1 className="display-5 fw-bold mb-2">Alerts</h1>
        </div>

        {props.user_alerts.length === 0 ? (
          <div className="d-flex justify-content-center">
            <BootstrapAlert variant="info" className="w-100" style={{ maxWidth: "500px" }}>
              No alerts available.
            </BootstrapAlert>
          </div>
        ) : (
          <div className="alerts-list mx-auto" style={{ maxWidth: "800px" }}>
            {props.user_alerts.map((user_alert) => (
              <Card
                key={user_alert.id}
                className={classNames("mb-3 border shadow-sm", {
                  "border-primary": !user_alert.is_read,
                })}
                style={{
                  opacity: user_alert.is_read ? 0.7 : 1,
                  backgroundColor: !user_alert.is_read ? "rgba(13, 110, 253, 0.05)" : undefined,
                }}
                role="button"
                tabIndex={0}
                onClick={() => handleAlertClick(user_alert.id)}
              >
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-start">
                    <div>
                      <Card.Title className="h5">{user_alert.alert.title}</Card.Title>
                      <Card.Subtitle className="text-muted small">
                        {formatDateTypical(user_alert.alert.datetime_created)}
                      </Card.Subtitle>
                    </div>
                    {!user_alert.is_read && (
                      <span
                        className="badge bg-primary"
                        style={{ whiteSpace: "nowrap", marginLeft: "0.5rem" }}
                      >
                        New
                      </span>
                    )}
                  </div>
                </Card.Body>
              </Card>
            ))}
          </div>
        )}
      </Container>

      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg" centered>
        {alertFetcher.data && (
          <>
            <Modal.Header closeButton>
              <Modal.Title className="fw-bold">{alertFetcher.data.alert.title}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <p className="text-muted small mb-4">
                {formatDateTypical(alertFetcher.data.alert.datetime_created)}
              </p>
              <div>
                <Markdown>{alertFetcher.data.alert.md_message}</Markdown>
              </div>
            </Modal.Body>
          </>
        )}
      </Modal>
    </Layout>
  );
}
