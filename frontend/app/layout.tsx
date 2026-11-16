import type { Metadata, Viewport } from "next";
import "./globals.css";

/*
  tasteskill build (design-taste-frontend 2.5), kind: place.
  deal: the client's own colours (start.mjs brand), per the brief "darker, clean, a bit casual":
  an evening momo joint, espresso-charcoal ground, cream ink, marigold accent (festival garlands),
  chili-red brand band; type fraunces (Fraunces with SOFT 100 for a friendlier serif / Figtree),
  radius square, hero split (the photograph framed beside the words), nav-split, footer-columns,
  rhythm colour-band, buttons arrow, mark petal, offer tall-small, type moment name (close-word on
  the brand band), moments word-highlight + photo-chapters.
  The kit (system.css, motion, layout, moments) is copied unchanged into public/assets.
*/

export const metadata: Metadata = {
  title: "Momo Mart: momo kitchen in Jhamsikhel, Lalitpur",
  description:
    "Hand-folded momos to eat at the counter or take home frozen, with achar and Ilam tea. Same-day delivery across the Kathmandu Valley.",
  openGraph: {
    type: "website",
    title: "Momo Mart: momo kitchen in Jhamsikhel, Lalitpur",
    description: "Hand-folded momos to eat at the counter or take home frozen, with achar and Ilam tea.",
    images: ["/assets/img/photo-f80246473-1440.webp"],
  },
  twitter: { card: "summary_large_image" },
  other: { "page-type": "place", "page-kind": "place", "site-kind": "other" },
};

export const viewport: Viewport = {
  themeColor: "#17120f",
  viewportFit: "cover",
};

// Set before first paint: the hero's words wait for motion.js (700 ms fallback),
// and moments know scripts will run (2.5 s fallback). From the kit's starter.
const HEAD_SCRIPT =
  "document.documentElement.classList.add('m-enter');setTimeout(()=>document.documentElement.classList.add('m-enter-done'),700);" +
  "document.documentElement.classList.add('mo-js');setTimeout(()=>document.documentElement.classList.add('mo-safe'),2500)";

const TOKENS = `:root {
  --p-bg: #17120f; --p-surface: #221b17; --p-ink: #f3eadd; --p-muted: #b9ab9b;
  --p-accent: #f2a93b; --p-accent-ink: #1b130d; --p-action: #f2a93b; --p-action-ink: #1b130d;
  --p-inv-bg: #a3302a; --p-inv-surface: #8e2823; --p-inv-ink: #fff3e6; --p-inv-muted: #f1cbbf;
  --p-inv-accent: #ffd38c; --p-inv-accent-ink: #5a1612; --p-inv-action: #fff3e6; --p-inv-action-ink: #8e2823;
  --font-display: "Fraunces", Georgia, serif;
  --font-text: "Figtree", system-ui, sans-serif;
  --display-weight: 400;
  --display-tracking: -0.02em;
  --display-axes: 'SOFT' 100, 'WONK' 1;
}`;

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      data-type="place"
      data-radius="square"
      data-buttons="arrow"
      data-motion=""
      suppressHydrationWarning
    >
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,400..600,0..100,0..1&family=Figtree:wght@400..600&display=swap"
        />
        <link rel="stylesheet" href="/assets/system.css" />
        <link rel="stylesheet" href="/assets/ui/cards.css" />
        <link rel="stylesheet" href="/assets/motion/motion.css" />
        <link rel="stylesheet" href="/assets/layout/layout.css" />
        <style dangerouslySetInnerHTML={{ __html: TOKENS }} />
        <script dangerouslySetInnerHTML={{ __html: HEAD_SCRIPT }} />
        <link rel="modulepreload" href="/assets/moments/moments.js" />
        <link rel="modulepreload" href="/assets/moments/lib.js" />
        <link rel="modulepreload" href="/assets/moments/photo-chapters/moment.js" />
        <link rel="modulepreload" href="/assets/moments/word-highlight/moment.js" />
      </head>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
