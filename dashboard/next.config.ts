import { NextConfig } from "next";

const config: NextConfig = {
  // Disable static export - use standard Next.js SSR/CSR
  // output: 'export',  // Commented out for dev mode
  images: {
    unoptimized: true,
  },
};

export default config;
