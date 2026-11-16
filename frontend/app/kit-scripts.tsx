"use client";

import { useEffect } from "react";

// The kit's scripts rewrite parts of the page (the phone menu, the moments, the hero
// entrance). They must run AFTER React has hydrated the server HTML, or React would
// find a DOM it didn't render and throw those changes away. So they load here, in
// order, once, from public/assets (unchanged copies of the skill's kit).
const SCRIPTS = ["/assets/system.js", "/assets/motion/motion.js", "/assets/layout/layout.js"];

export function KitScripts() {
  useEffect(() => {
    if (document.documentElement.dataset.kitLoaded) return;
    document.documentElement.dataset.kitLoaded = "1";

    const load = (i: number) => {
      if (i >= SCRIPTS.length) return;
      const s = document.createElement("script");
      s.type = "module";
      s.src = SCRIPTS[i];
      s.onload = () => load(i + 1);
      document.body.appendChild(s);
    };
    load(0);
  }, []);

  return null;
}
