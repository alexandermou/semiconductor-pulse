import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {title:"Semiconductor Pulse",description:"Session-aware semiconductor prices, news and a persistent update archive."};
export default function RootLayout({children}:Readonly<{children:React.ReactNode}>){return <html lang="en"><body>{children}</body></html>}
