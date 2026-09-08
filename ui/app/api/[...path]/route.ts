import { NextRequest } from "next/server";

const API_ORIGIN = (process.env.HEDGEKNIGHT_API_URL || "http://localhost:8000").replace(/\/$/, "");

async function proxy(request: NextRequest) {
  const upstreamPath = request.nextUrl.pathname + request.nextUrl.search;
  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);
  const response = await fetch(`${API_ORIGIN}${upstreamPath}`, {
    method: request.method,
    headers,
    body: request.method === "GET" || request.method === "HEAD" ? undefined : await request.arrayBuffer(),
    cache: "no-store",
  });
  return new Response(response.body, {status: response.status, headers: {"content-type": response.headers.get("content-type") || "application/json"}});
}

export const GET = proxy;
export const POST = proxy;
