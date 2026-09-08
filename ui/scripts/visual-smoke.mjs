import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";

const browser = await chromium.launch({ headless: true });
await mkdir("../.impeccable/review", { recursive: true });
const existing = await fetch("http://localhost:8000/api/positions/active").then(r => r.json());
if (existing?.state === "open") {
  await fetch(`http://localhost:8000/api/positions/${existing.position_id}/unwind-simulate`, { method: "POST" });
}

async function capture(viewport, file) {
  const page = await browser.newPage({ viewport });
  const errors = [];
  page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
  await page.goto("http://localhost:3000", { waitUntil: "networkidle" });
  await page.screenshot({ path: `../.impeccable/review/${file}`, fullPage: true });
  if (viewport.width > 700) {
    await page.locator("nav").getByRole("button", { name: "Create hedge" }).click();
    await page.getByRole("button", { name: /Calculate & risk-check/ }).click();
    await page.getByText("RISK APPROVED").waitFor();
    await page.screenshot({ path: "../.impeccable/review/create.png", fullPage: true });
    await page.getByRole("button", { name: "Confirm this exact plan" }).click();
    await page.getByRole("button", { name: /Simulate hedge execution/ }).click();
    await page.getByText("Effective hedge").waitFor();
    const effective = await page.locator(".monitor-hero strong").first().textContent();
    if (effective !== "50.00%") throw new Error(`Unexpected effective hedge: ${effective}`);
  }
  if (errors.length) throw new Error(`Browser console errors: ${errors.join(" | ")}`);
  await page.close();
}

await capture({ width: 1440, height: 1000 }, "desktop.png");
await capture({ width: 390, height: 844 }, "mobile.png");
await browser.close();
console.log("desktop, create, mobile, and canonical interaction inspected");
