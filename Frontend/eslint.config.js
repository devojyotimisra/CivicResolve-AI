import unusedImports from "eslint-plugin-unused-imports";

export default [
  {
    files: ["**/*.js", "**/*.jsx"],
    languageOptions: {
      parserOptions: {
        ecmaFeatures: {
          jsx: true
        }
      }
    },
    plugins: {
      "unused-imports": unusedImports,
    },
    rules: {
      "no-multiple-empty-lines": ["error", { "max": 1, "maxEOF": 0 }],
      "unused-imports/no-unused-imports": "error",
      "no-unused-vars": ["warn", { 
        "vars": "all", 
        "args": "after-used", 
        "ignoreRestSiblings": true,
        "argsIgnorePattern": "^_"
      }],
    }
  }
];
