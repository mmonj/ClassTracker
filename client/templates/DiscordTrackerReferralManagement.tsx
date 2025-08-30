import React, { useState } from "react";

import { CSRFToken, templates } from "@reactivated";
import { Badge, Button, Card, Col, Container, Row, Table } from "react-bootstrap";

import { faCheck, faCopy } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { formatDateTypical } from "@client/utils";

import { ReferralsPagination } from "@client/components/DiscordTrackerReferralManagement";
import { Navbar } from "@client/components/discord_tracker/Navbar";
import { FormFieldset } from "@client/components/forms/FormFieldset";
import { Layout } from "@client/layouts/Layout";

export function Template({
  referral_form,
  referrals,
  pagination,
}: templates.DiscordTrackerReferralManagement) {
  function getStatusBadge(referral: (typeof referrals)[0]) {
    if (referral.num_uses >= referral.max_uses) {
      return <Badge bg="success">Fully Redeemed</Badge>;
    }
    if (referral.num_uses > 0) {
      return <Badge bg="warning">Partially Redeemed</Badge>;
    }
    if (referral.is_expired === true) {
      return <Badge bg="danger">Expired</Badge>;
    }
    return <Badge bg="primary">Active</Badge>;
  }

  function formatExpiryTimeframe(timeframe: string): string {
    const timeframeMap: { [key: string]: string } = {
      "1w": "1 Week",
      "2w": "2 Weeks",
      "1m": "1 Month",
      "3m": "3 Months",
      permanent: "Never",
    };
    return timeframeMap[timeframe] || timeframe;
  }

  function generatePaginationUrl(page: number): string {
    if (typeof window === "undefined") {
      return `?page=${page}`;
    }
    const url = new URL(window.location.href);
    url.searchParams.set("page", page.toString());
    return url.toString();
  }

  return (
    <Layout title="Referral Management" Navbar={Navbar}>
      <Container className="py-4 px-0">
        <Row>
          <Col>
            <h1 className="mb-4">Referral Management</h1>
            {/* create referral form */}
            <Card className="mb-4 p-2">
              <Card.Header>
                <h5 className="mb-0">Create New Referral</h5>
              </Card.Header>
              <Card.Body>
                <form method="POST">
                  <CSRFToken />
                  <FormFieldset form={referral_form} />
                  <Button type="submit" variant="primary">
                    Create Referral
                  </Button>
                </form>
              </Card.Body>
            </Card>

            {/* referrals list */}
            <Card className="p-2">
              <Card.Header>
                <h5 className="mb-0">Your Created Referrals</h5>
              </Card.Header>
              <Card.Body>
                {referrals.length === 0 ? (
                  <p className="text-muted">You haven't created any referrals yet.</p>
                ) : (
                  <Table responsive>
                    <thead>
                      <tr>
                        <th>Status</th>
                        <th>Uses</th>
                        <th>Created</th>
                        <th>Expires</th>
                        <th>Copy URL</th>
                      </tr>
                    </thead>
                    <tbody>
                      {referrals.map((referral) => (
                        <tr key={referral.id}>
                          <td>{getStatusBadge(referral)}</td>
                          <td>
                            {referral.num_uses} /{" "}
                            {referral.max_uses === 0 ? "∞" : referral.max_uses}
                          </td>
                          <td>{formatDateTypical(referral.datetime_created)}</td>
                          <td>
                            {referral.expiry_timeframe
                              ? formatExpiryTimeframe(referral.expiry_timeframe)
                              : referral.datetime_expires !== null &&
                                  referral.datetime_expires !== ""
                                ? formatDateTypical(referral.datetime_expires)
                                : "Never"}
                          </td>
                          <td>
                            <CopyUrlButton url={referral.url} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                )}

                <ReferralsPagination
                  pagination={pagination}
                  generatePaginationUrl={generatePaginationUrl}
                />
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </Layout>
  );
}

function CopyUrlButton({ url }: { url: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      const fullUrl = `${window.location.origin}${url}`;
      await navigator.clipboard.writeText(fullUrl);
      setCopied(true);

      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy URL:", err);
    }
  };

  return (
    <Button
      variant={copied ? "success" : "outline-primary"}
      className="d-flex align-items-center gap-1"
      size="sm"
      onClick={handleCopy}
      title={copied ? "Copied!" : "Copy referral URL"}
    >
      <span>Copy URL</span>
      <FontAwesomeIcon icon={copied ? faCheck : faCopy} />
    </Button>
  );
}
