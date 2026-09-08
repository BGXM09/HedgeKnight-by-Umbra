import { NextRequest, NextResponse } from "next/server";

const scenarios = [
  ["valid-50", "Valid 50% · 24 hours", 50, 24, 2, "approved"],
  ["leverage-10x", "10× leverage", 50, 24, 10, "blocked"],
  ["over-hedge", "125% hedge", 125, 24, 2, "blocked"],
  ["stale-evidence", "Stale market evidence", 50, 24, 2, "blocked"],
  ["unverified-source", "Unverified connected source", 50, 24, 2, "blocked"],
  ["funding-limit", "Funding cost above limit", 100, 168, 1, "blocked"],
  ["expired-plan", "Expired plan", 50, 24, 2, "blocked"],
  ["duplicate-plan", "Duplicate execution", 50, 24, 2, "blocked"],
  ["kill-switch", "Kill switch enabled", 50, 24, 2, "blocked"],
  ["valid-unwind", "Valid reduce-only unwind", 50, 24, 2, "approved"],
].map(([id,label,ratio,duration,leverage,outcome])=>({id,label,ratio,duration,leverage,outcome}));

const pathOf=(request:NextRequest)=>request.nextUrl.pathname.replace(/^\/api\//,"");
const json=(body:unknown,status=200)=>NextResponse.json(body,{status});
const unavailable=()=>json({error:{code:"BINANCE_EVIDENCE_UNAVAILABLE",message:"Fresh Binance MCP evidence has not been ingested into the production API."}},503);

export async function GET(request:NextRequest){
  const path=pathOf(request);
  if(path==="status") return json({product:"HedgeKnight — by Umbra",mode:"connected-read-only",execution:"simulated_only",market_source:"unavailable",kill_switch:false,live_execution:"unavailable",time:new Date().toISOString()});
  if(path==="market") return json({verification:"unavailable",source:"Binance MCP evidence has not been ingested",retrieved_at:new Date().toISOString(),source_tool:null});
  if(path==="exposure") return json({spot_bnb:"0.000",live_short_bnb:"0.000",simulated_short_bnb:"0.000",net_bnb:"0.000",effective_hedge_percent:"0.00",futures_usdt_available:"0",evidence_verification:"unavailable",mode:"connected-read-only",execution:"simulated"});
  if(path==="positions/active") return json(null);
  if(path==="receipts") return json([]);
  if(path==="scenarios") return json(scenarios);
  return json({error:{code:"NOT_FOUND",message:"Unknown API endpoint."}},404);
}

export async function POST(request:NextRequest){
  const path=pathOf(request);
  if(path==="settings/kill-switch") return json({kill_switch:false});
  return unavailable();
}
