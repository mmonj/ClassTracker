import { defineConfig } from "eslint/config";
import { default as reactivated } from "reactivated/dist/eslint.config";

type Config = ReturnType<typeof defineConfig>;

export default defineConfig([
  ...(reactivated as Config[]),
  {
    rules: {
      "react/no-unescaped-entities": "off",
      "unused-imports/no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
      "@typescript-eslint/no-use-before-define": "off",
      "import/order": "off",
    },
  },
]);
