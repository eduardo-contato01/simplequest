import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";

export async function generateMetadata(): Promise<Metadata> {
  const requestHeaders = await headers();
  const host = requestHeaders.get("host") ?? "localhost:5173";
  const protocol = requestHeaders.get("x-forwarded-proto") ?? (host.startsWith("localhost") ? "http" : "https");
  const base = `${protocol}://${host}`;
  const description = "Pesquise questões de concursos militares e monte simulados em poucos minutos.";
  return {
    metadataBase: new URL(base),
    title: "SimpleQuest — Banco de questões",
    description,
    icons: { icon: "/favicon.svg", shortcut: "/favicon.svg" },
    openGraph: {
      title: "SimpleQuest — Questões certas. Provas prontas.",
      description,
      images: [{ url: `${base}/og.png`, width: 1200, height: 630, alt: "SimpleQuest — Questões certas. Provas prontas." }],
      locale: "pt_BR",
      type: "website",
    },
    twitter: { card: "summary_large_image", title: "SimpleQuest", description, images: [`${base}/og.png`] },
  };
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="pt-BR"><body>{children}</body></html>;
}
