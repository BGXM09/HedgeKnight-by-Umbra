import "@fontsource-variable/manrope/index.css";
import "@fontsource-variable/space-grotesk/index.css";
import "./globals.css";
import "./landing.css";
export const metadata = { title: "HedgeKnight — by Umbra", description: "AI-powered portfolio hedging through Binance Agent OS." };
export default function RootLayout({children}:{children:React.ReactNode}) { return <html lang="en"><body>{children}</body></html>; }
