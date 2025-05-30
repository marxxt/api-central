// File: rate_limit.ts
// Description: Supabase Edge Function to limit user actions using Upstash Redis

import { serve } from "https://deno.land/std@0.131.0/http/server.ts";
import { Redis } from "https://esm.sh/@upstash/redis@1.20.2";

const redis = new Redis({
  url: Deno.env.get("UPSTASH_REDIS_REST_URL")!,
  token: Deno.env.get("UPSTASH_REDIS_REST_TOKEN")!,
});

const RATE_LIMIT = 5;
const WINDOW_SECONDS = 60;

serve(async (req) => {
  const { action_type = "comment", identifier } = await req.json();

  if (!identifier) {
    return new Response(JSON.stringify({ error: "Missing identifier" }), {
      status: 400,
    });
  }

  const key = `rate:${action_type}:${identifier}`;
  const count = await redis.incr(key);

  if (count === 1) {
    await redis.expire(key, WINDOW_SECONDS);
  }

  if (count > RATE_LIMIT) {
    return new Response(JSON.stringify({
      error: "Rate limit exceeded",
      remaining: 0,
      reset_in: await redis.ttl(key),
    }), {
      status: 429,
    });
  }

  return new Response(JSON.stringify({
    allowed: true,
    remaining: RATE_LIMIT - count,
    reset_in: await redis.ttl(key),
  }), {
    status: 200,
  });
});
