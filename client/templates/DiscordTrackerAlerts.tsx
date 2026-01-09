import React, { useContext, useState } from "react";

import { Alert as BootstrapAlert, Card, Container, Modal } from "react-bootstrap";

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

    await alertFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("discord_tracker:get_alert_details", { alert_id: alertId }),
        context.csrf_token,
        "GET",
      ),
    );
  }

  return (
    <Layout title="Alerts" description="View your notifications and alerts" Navbar={Navbar}>
      <Container className="py-4">
        <h1 className="mb-4 text-center">Alerts</h1>

        {props.alerts.length === 0 ? (
          <BootstrapAlert variant="info">No alerts available.</BootstrapAlert>
        ) : (
          <div className="alerts-list">
            {props.alerts.map((alert) => (
              <Card
                key={alert.id}
                className="mb-3"
                style={{ cursor: "pointer" }}
                onClick={() => handleAlertClick(alert.id)}
              >
                <Card.Body>
                  <Card.Title>{alert.title}</Card.Title>
                  <Card.Subtitle className="mb-2 text-muted">
                    {formatDateTypical(alert.datetime_created)}
                  </Card.Subtitle>
                </Card.Body>
              </Card>
            ))}
          </div>
        )}
      </Container>

      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        {alertFetcher.data && (
          <>
            <Modal.Header closeButton>
              <Modal.Title>{alertFetcher.data.alert.title}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <div>
                <p className="text-muted">
                  {formatDateTypical(alertFetcher.data.alert.datetime_created)}
                </p>
                <div
                  style={{
                    whiteSpace: "pre-wrap",
                    wordWrap: "break-word",
                  }}
                >
                  {alertFetcher.data.alert.message}
                </div>
              </div>
            </Modal.Body>
          </>
        )}
      </Modal>
    </Layout>
  );
}
