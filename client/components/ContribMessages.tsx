import React, { ContextType, useContext, useState } from "react";

import { Context } from "@reactivated";

export function ContribMessages() {
  const djangoContext = useContext(Context);

  return (
    <>
      {djangoContext.messages.length > 0 && (
        <section className="server-messages">
          <ul className="list-group fw-semibold text-center" style={{ listStyle: "none" }}>
            {djangoContext.messages.map((message, idx) => (
              <Message key={idx} message={message} />
            ))}
          </ul>
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
    <li className={`alert alert-${alert_type} rounded-0 position-relative mb-2`}>
      <span>{message.message}</span>
      <button
        type="button"
        className="btn-close btn-close-white position-absolute top-0 end-0 mt-2 me-2"
        aria-label="Close"
        onClick={() => setIsShown(false)}
      ></button>
    </li>
  );
}
