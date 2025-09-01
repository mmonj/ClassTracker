import React, { type JSX } from "react";

import { Context } from "@reactivated";

import classNames from "classnames";

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
  Navbar?: () => JSX.Element;
}

export const Layout = ({
  Navbar,
  djangoStaticStylePaths = [],
  baseClassName = "mw-80-rem mx-auto p-2 px-3",
  className = "",
  ...props
}: Props) => {
  const djangoContext = React.useContext(Context);
  const stylePaths = [
    "styles/bs-dark/main.css",
    "styles/reset.css",
    "styles/shared.css",
    "styles/react-select/react-select.css",
  ];

  return (
    <html>
      <head>
        <meta charSet="utf-8" />
        <title>{props.title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link
          rel="icon"
          type="image/svg+xml"
          href={`${djangoContext.STATIC_URL}public/favicon.svg`}
        />

        {/* meta tags */}
        <meta property="og:title" content="Class Cords" />
        <meta
          property="og:description"
          content="Find and join Discord servers for your college classes"
        />
        <meta property="og:image" content={`${djangoContext.STATIC_URL}public/logo-500x471.png`} />
        <meta property="og:type" content="website" />

        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap"
          rel="stylesheet"
        />

        {stylePaths.map((stylePath, idx) => (
          <link
            key={idx}
            rel="stylesheet"
            type="text/css"
            href={djangoContext.STATIC_URL + stylePath}
          />
        ))}

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
      </head>
      <body>
        {Navbar && (
          <header>
            <Navbar />
          </header>
        )}
        <main>
          <ContribMessages />
          <section id="content" className={classNames(baseClassName, className)}>
            {props.children}
          </section>
        </main>
      </body>
    </html>
  );
};
