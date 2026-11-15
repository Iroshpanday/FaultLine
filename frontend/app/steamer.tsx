// A bamboo steamer seen from above, seven momos inside, steam rising.
// Drawn in SVG so the hero needs no image files.

const MOMO_SPOTS: [number, number][] = [
  [200, 268],
  ...[0, 60, 120, 180, 240, 300].map((deg): [number, number] => {
    const r = (deg * Math.PI) / 180;
    return [Math.round(200 + 96 * Math.cos(r)), Math.round(268 + 96 * Math.sin(r))];
  }),
];

const PLEATS = [0, 51, 103, 154, 206, 257, 309];

export function Steamer({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 400 460" className={className} role="img" aria-label="Momos in a bamboo steamer">
      <defs>
        <clipPath id="steamer-floor">
          <circle cx="200" cy="268" r="150" />
        </clipPath>
      </defs>

      <g className="steam" fill="none" stroke="#9fb3aa" strokeWidth="7" strokeLinecap="round">
        <path d="M150 96 c-14 -16 14 -28 0 -46 s14 -28 0 -44" />
        <path d="M200 92 c-14 -16 14 -28 0 -46 s14 -28 0 -44" />
        <path d="M250 96 c-14 -16 14 -28 0 -46 s14 -28 0 -44" />
      </g>

      {/* rim */}
      <circle cx="200" cy="268" r="176" fill="#d9c9a0" stroke="#b8a370" strokeWidth="4" />
      <circle cx="200" cy="268" r="164" fill="none" stroke="#c6b282" strokeWidth="3" />
      <circle cx="200" cy="268" r="156" fill="#c9b484" stroke="#b8a370" strokeWidth="3" />

      {/* woven floor */}
      <g clipPath="url(#steamer-floor)" stroke="#b39d68" strokeWidth="2" opacity="0.55">
        {Array.from({ length: 22 }, (_, i) => {
          const o = 40 + i * 16;
          return (
            <g key={i}>
              <line x1={o} y1="100" x2={o - 200} y2="440" />
              <line x1={o - 200} y1="100" x2={o} y2="440" />
            </g>
          );
        })}
      </g>

      {MOMO_SPOTS.map(([x, y], i) => (
        <g key={i} transform={`translate(${x} ${y}) rotate(${i * 23})`}>
          <ellipse cx="4" cy="8" rx="45" ry="42" fill="#173b34" opacity="0.1" />
          <circle r="45" fill="#fbf9f3" stroke="#e5dcc8" strokeWidth="2" />
          {PLEATS.map((a) => (
            <path
              key={a}
              d="M0,-6 C10,-13 16,-25 10,-38"
              fill="none"
              stroke="#ddd2b9"
              strokeWidth="2.5"
              strokeLinecap="round"
              transform={`rotate(${a})`}
            />
          ))}
          <circle r="6.5" fill="#efe6d2" stroke="#ddd2b9" strokeWidth="1.5" />
        </g>
      ))}
    </svg>
  );
}
