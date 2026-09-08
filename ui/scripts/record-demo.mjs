import { chromium } from "playwright";
import path from "node:path";

const output = path.resolve("../submission/hedgeknight-demo.webm");
const baseUrl = process.env.DEMO_URL || "http://127.0.0.1:3000";
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  recordVideo: { dir: path.resolve("../submission/.video-tmp"), size: { width: 1440, height: 900 } },
});
const page = await context.newPage();
const pause = ms => page.waitForTimeout(ms);

const installCaption = () => page.evaluate(() => {
  document.querySelectorAll("#demo-caption").forEach(element => element.remove());
  const caption = document.createElement("div");
  caption.id = "demo-caption";
  Object.assign(caption.style, {
    position: "fixed", left: "50%", bottom: "28px", transform: "translateX(-50%)",
    zIndex: "9999", maxWidth: "960px", padding: "14px 22px", borderRadius: "8px",
    color: "#f4f0e5", background: "rgba(6,8,10,.92)", border: "1px solid #f0b90b",
    font: "600 22px/1.35 Manrope, sans-serif", textAlign: "center",
    boxShadow: "0 12px 36px rgba(0,0,0,.45)", pointerEvents: "none"
  });
  document.body.appendChild(caption);
});
await page.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
await installCaption();
const caption = async text => { await page.locator("#demo-caption").evaluate((el,value)=>el.textContent=value,text); };

await caption("HedgeKnight turns a protection request into a bounded, simulated BNB hedge.");
await pause(4500);
await caption("Keep the asset. Cut the exposure. Every financial action in this demo is simulated.");
await pause(4500);
await page.getByRole("link", { name: /Run the 60-second demo/ }).click();
await page.waitForLoadState("networkidle");
await installCaption();
await caption("The dashboard begins with a 10 BNB demo portfolio and clearly labelled replay market data.");
await pause(4000);
await page.getByRole("button", { name: "Create hedge" }).first().click();
await caption("Request: hedge 50% of 10 BNB for 24 hours, with a maximum of 2× leverage.");
await pause(5000);
await page.getByRole("button", { name: /Calculate & risk-check/ }).click();
await pause(1200);
await caption("HedgeKnight calculates the exact 5 BNB short, margin, fees, and projected funding.");
await pause(5000);
await caption("Thirteen deterministic checks approve or block the plan before execution.");
await pause(5000);
await page.getByRole("button", { name: "Confirm this exact plan" }).click();
await pause(1000);
await caption("The user confirms one exact, short-lived plan ID.");
await pause(3500);
await page.getByRole("button", { name: /Simulate hedge execution/ }).click();
await pause(1400);
await caption("Execution is simulated—no wallet, funds, or live order is involved.");
await pause(5000);
await caption("The monitor now shows 50% protection and 5 BNB remaining net exposure.");
await pause(5000);
await page.getByRole("button", { name: "Receipts" }).click();
await pause(800);
await page.locator("summary").first().click();
await caption("A tamper-evident receipt preserves the evidence, calculation, risk decision, and result.");
await pause(5500);
await page.getByRole("button", { name: "Monitor" }).click();
await pause(700);
await page.getByRole("button", { name: /Prepare & simulate unwind/ }).click();
await pause(1200);
await caption("A bounded reduce-only unwind closes the simulated hedge and seals a linked receipt.");
await pause(5000);
await caption("HedgeKnight by Umbra — portfolio protection that is inspectable, bounded, and provable.");
await pause(4500);

const video = page.video();
await context.close();
await video.saveAs(output);
await browser.close();
console.log(output);
