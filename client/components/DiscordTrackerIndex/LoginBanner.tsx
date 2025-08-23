import React, { useState } from "react";

import { CSRFToken, reverse } from "@reactivated";
import { Alert, Button } from "react-bootstrap";

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
        <FontAwesomeIcon icon={faDiscord} className="me-2" />
        <span>Sign in with Discord to access further invites.</span>
      </div>
      <form method="POST" action={reverse("discord_login")}>
        <CSRFToken />
        <Button type="submit" variant="outline-primary" size="sm" className="ms-3 flex-shrink-0">
          <FontAwesomeIcon icon={faDiscord} className="me-1" />
          Sign in
        </Button>
      </form>
    </Alert>
  );
}
