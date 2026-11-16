import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    // The tasteskill design kit, copied unchanged from the skill: not our code to lint.
    "public/assets/**",
  ]),
  {
    // The page uses the kit's own markup: plain <img srcset> (pre-sized WebP files) and the
    // kit's stylesheets and Google Fonts link in <head>, instead of next/image and next/font.
    files: ["app/page.tsx", "app/layout.tsx"],
    rules: {
      "@next/next/no-img-element": "off",
      "@next/next/no-css-tags": "off",
      "@next/next/no-page-custom-font": "off",
    },
  },
]);

export default eslintConfig;
