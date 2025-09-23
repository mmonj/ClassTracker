import React, { ContextType, useContext, useState } from "react";

import { Alert } from "react-bootstrap";

import { Context } from "@reactivated";

export function ContribMessages() {
  const djangoContext = useContext(Context);

  return (
    <>
      {djangoContext.messages.length > 0 && (
        <section className="server-messages">
          {djangoContext.messages.map((message, idx) => (
            <Message key={idx} message={message} />
          ))}
        </section>
      )}
    </>
  );
}

function Message({ message }: { message: ContextType<typeof Context>["messages"][number] }) {
  const [isShown, setIsShown] = useState(true);

  if (!isShown) {
    return null;
  }

  const alert_type = message.level_tag === "error" ? "danger" : message.level_tag;

  return (
    <Alert
      variant={alert_type}
      dismissible
      onClose={() => setIsShown(false)}
      className="rounded-0 mb-1 fw-semibold text-center btn-close-white"
    >
      {message.message}
    </Alert>
  );
}
