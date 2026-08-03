import express from "express";
import bodyParser from "body-parser";
import { Contract, ElectrumNetworkProvider, Network } from "cashscript";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const artifactPath = path.resolve(
  __dirname,
  "../frontend/chatpay_frontend/src/contracts/UserWallet.json"
);

let UserWalletArtifact;
try {
  UserWalletArtifact = JSON.parse(fs.readFileSync(artifactPath, "utf-8"));
} catch (err) {
  console.error(`[Payment Service] Could not load artifact at ${artifactPath}:`, err.message);
  process.exit(1);
}

const app = express();
app.use(bodyParser.json());

const networkMode = process.env.BCH_NETWORK === "chipnet" ? Network.CHIPNET : Network.MAINNET;

app.post("/send-message-payment", async (req, res) => {
  try {
    const { userName, userId, roomContractAddress, amountSats } = req.body;
    console.log("[Payment Service] Payment request payload:", req.body);
    if (!userName || !userId || !roomContractAddress) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    const provider = new ElectrumNetworkProvider(networkMode);
    const userIdBytes = new TextEncoder().encode(String(userId));
    const userWallet = new Contract(
      UserWalletArtifact,
      [userName, userIdBytes],
      { provider }
    );

    const txResult = await userWallet.functions
      .transfer(userName, userIdBytes)
      .to(roomContractAddress, BigInt(amountSats || 1800))
      .withHardcodedFee(1000n)
      .send();

    console.log("[Payment Service] Payment sent to contract address:", roomContractAddress);
    console.log("[Payment Service] Transaction result:", txResult);

    res.json({ success: true, txid: txResult?.txid?.toString() });
  } catch (e) {
    console.error("[Payment Service] Error:", e);
    res.status(500).json({ error: e.message });
  }
});

const PORT = process.env.PORT || 5001;
app.listen(PORT, () => {
  console.log(`Message payment service running on port ${PORT} (${networkMode})`);
});
