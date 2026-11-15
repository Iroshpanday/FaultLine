import type { Metadata, Viewport } from "next";
import { Bricolage_Grotesque } from "next/font/google";
import "./globals.css";

const bricolage = Bricolage_Grotesque({
  variable: "--font-bricolage",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Momo Mart: frozen momos, achar and tea, delivered in Kathmandu",
  description:
    "Hand-folded frozen momos, homemade achar and Himalayan tea, delivered across Kathmandu Valley. A demo store with an AI order-help assistant.",
};

export const viewport: Viewport = {
  themeColor: "#173b34",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${bricolage.variable} h-full`}>
      <body className="min-h-full">{children}</body>
    </html>
  );
}
