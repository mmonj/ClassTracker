import React, { useContext } from "react";

import { Card, Col, Container, Row } from "react-bootstrap";

import { CSRFToken, Context, interfaces, reverse, templates } from "@reactivated";

import { faDiscord } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { ButtonWithSpinner } from "@client/components/ButtonWithSpinner";
import { Navbar } from "@client/components/discord_tracker/Navbar";
import { useFetch } from "@client/hooks/useFetch";
import { Layout } from "@client/layouts/Layout";
import { fetchByReactivated } from "@client/utils";

export function Template(_props: templates.DiscordTrackerLogin) {
  const context = useContext(Context);
  const referralFetcher = useFetch<interfaces.BlankResponse>();

  async function handleFormSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget as HTMLFormElement;

    const urlParams = new URLSearchParams(window.location.search);
    const referralCode = urlParams.get("referral");

    if (referralCode === null || referralCode.trim() === "") {
      // go on with normal form submission
      form.submit();
      return;
    }

    const result = await referralFetcher.fetchData(() =>
      fetchByReactivated(
        reverse("discord_tracker:ajax_referral_redeem") +
          `?referral=${encodeURIComponent(referralCode)}`,
        context.csrf_token,
        "GET",
      ),
    );

    if (!result.ok) {
      console.error("Failed to redeem referral code:", result.errors);
    }

    // referral code applied - go on with normal form submission
    form.submit();
  }

  return (
    <Layout
      title="Discord Login"
      description="Log in to your Discord account - Class Cords"
      Navbar={Navbar}
    >
      <Container className="d-flex align-items-center justify-content-center min-vh-100 px-0">
        <Row className="w-100">
          <Col xs={12} md={6} lg={4} className="mx-auto">
            <Card className="shadow-lg border-0">
              <Card.Body className="text-center p-5">
                <div className="mb-4">
                  <FontAwesomeIcon icon={faDiscord} size="4x" className="text-primary" />
                </div>
                <h2 className="h3 mb-3">Welcome to Class Cords</h2>
                <p className="text-muted mb-4">
                  Sign in with your Discord account to access the private class discord servers.
                </p>

                <form method="POST" action={reverse("discord_login")} onSubmit={handleFormSubmit}>
                  <CSRFToken />
                  <ButtonWithSpinner
                    className="btn btn-primary btn-lg w-100 mb-3"
                    type="submit"
                    spinnerVariant="dark"
                    isLoadingState={referralFetcher.isLoading}
                    spinnerSize="sm"
                  >
                    <FontAwesomeIcon icon={faDiscord} className="me-2" />
                    Sign in with Discord
                  </ButtonWithSpinner>
                </form>
                <div className="text-center">
                  <small className="text-muted">
                    In order to be able to sign up, you must get a referral from another user.
                  </small>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </Layout>
  );
}
