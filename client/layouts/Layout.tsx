import "/static/styles/bs-dark.css";
import "/static/styles/reset.css";
import "/static/styles/shared.css";

import React from "react";

import { Context } from "@reactivated";
import { Helmet } from "react-helmet-async";

import { ContribMessages } from "@client/components/ContribMessages";

type TDjangoBasePathStr = string;

interface IExternalStyles {
  src: string;
  integrity?: string;
}

interface Props {
  title: string;
  children: React.ReactNode;
  baseClassName?: string;
  className?: string;
  djangoStaticStylePaths?: TDjangoBasePathStr[];
  extraExternalStyles?: IExternalStyles[];
  Navbar: () => JSX.Element;
}

export const Layout = ({
  Navbar,
  djangoStaticStylePaths = [],
  baseClassName = "mw-80-rem mx-auto p-2 px-3",
  className = "",
  ...props
}: Props) => {
  const djangoContext = React.useContext(Context);

  return (
    <>
      <Helmet>
        <meta charSet="utf-8" />
        <title>{props.title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link
          rel="icon"
          type="image/x-icon"
          href={`${djangoContext.STATIC_URL}public/favicon.png`}
        />

        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap"
          rel="stylesheet"
        />

        {djangoStaticStylePaths.map((staticBasePath, idx) => (
          <link
            key={idx}
            rel="stylesheet"
            type="text/css"
            href={djangoContext.STATIC_URL + staticBasePath}
          />
        ))}

        {props.extraExternalStyles?.map((style, idx) => (
          <link
            key={idx}
            rel="stylesheet"
            href={style.src}
            integrity={style.integrity}
            crossOrigin=""
          />
        ))}
      </Helmet>
      <header>
        <Navbar />
      </header>
      <main>
        <ContribMessages />
        <section id="content" className={baseClassName + " " + className}>
          {props.children}
        </section>
      </main>
    </>
  );
};
