import React, { useState } from "react";

import { Alert, Button } from "react-bootstrap";

import { reverse } from "@reactivated";

import { faDiscord } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

interface LoginBannerProps {
  className?: string;
}

export function LoginBanner({ className = "" }: LoginBannerProps) {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) {
    return null;
  }

  return (
    <Alert
      variant="info"
      className={`d-flex align-items-center justify-content-between mb-4 btn-close-white ${className}`}
      dismissible
      onClose={() => setIsVisible(false)}
    >
      <div className="d-flex align-items-center">
        <span>Sign in with Discord to access private class servers</span>
      </div>
      <Button
        href={reverse("discord_tracker:login")}
        variant="outline-primary"
        size="sm"
        className="ms-3 flex-shrink-0 sign-in"
      >
        <FontAwesomeIcon icon={faDiscord} className="me-1" />
        Sign in
      </Button>
    </Alert>
  );
}
