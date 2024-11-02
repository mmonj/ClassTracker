module.exports = {
  extends: ["./node_modules/reactivated/dist/eslintrc.cjs"],
  rules: {
    "react/no-unescaped-entities": "off",
    "unused-imports/no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
    "@typescript-eslint/no-use-before-define": "off",
  },
};
