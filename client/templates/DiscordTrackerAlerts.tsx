import React, { useContext, useState } from "react";

import { Alert as BootstrapAlert, Card, Container, Modal } from "react-bootstrap";
import Markdown from "react-markdown";

import { Context, interfaces, reverse, templates } from "@reactivated";

import { Navbar } from "@client/components/discord_tracker/Navbar";
import { useFetch } from "@client/hooks/useFetch";
import { Layout } from "@client/layouts/Layout";
import { fetchByReactivated, formatDateTypical } from "@client/utils";

export function Template(props: templates.DiscordTrackerAlerts) {
  const [showModal, setShowModal] = useState(false);
  const context = useContext(Context);

  const alertFetcher = useFetch<interfaces.GetAlertDetailsResponse>();

  async function handleAlertClick(alertId: number) {
    setShowModal(true);

    const result = await alertFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("discord_tracker:get_alert_details", { alert_id: alertId }),
        context.csrf_token,
        "GET",
      ),
    );

    // mark alert as read
    if (result.ok) {
      await fetchByReactivated(
        reverse("discord_tracker:mark_alert_as_read", { user_alert_id: alertId }),
        context.csrf_token,
        "PUT",
      );
    }
  }

  return (
    <Layout title="Alerts" description="View your notifications and alerts" Navbar={Navbar}>
      <Container className="py-5">
        <div className="text-center mb-5">
          <h1 className="display-5 fw-bold mb-2">Alerts</h1>
        </div>

        {props.alerts.length === 0 ? (
          <div className="d-flex justify-content-center">
            <BootstrapAlert variant="info" className="w-100" style={{ maxWidth: "500px" }}>
              No alerts available.
            </BootstrapAlert>
          </div>
        ) : (
          <div className="alerts-list mx-auto" style={{ maxWidth: "800px" }}>
            {props.alerts.map((alert) => (
              <Card
                key={alert.id}
                className="mb-3 border shadow-sm"
                role="button"
                tabIndex={0}
                onClick={() => handleAlertClick(alert.id)}
              >
                <Card.Body>
                  <Card.Title className="h5">{alert.alert.title}</Card.Title>
                  <Card.Subtitle className="text-muted small">
                    {formatDateTypical(alert.alert.datetime_created)}
                  </Card.Subtitle>
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
