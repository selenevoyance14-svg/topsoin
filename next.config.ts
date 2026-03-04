import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  outputFileTracingIncludes: {
    "/**": ["./content/**/*.mdx"],
  },
};

export default nextConfig;
