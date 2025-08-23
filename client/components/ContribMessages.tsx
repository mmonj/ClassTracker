import React, { ContextType, useContext, useState } from "react";

import { Context } from "@reactivated";
import { Alert } from "react-bootstrap";

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
      className="rounded-0 mb-2 fw-semibold text-center btn-close-white"
    >
      {message.message}
    </Alert>
  );
}
