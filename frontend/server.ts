import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI, Type } from "@google/genai";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(express.json());

const PORT = 3000;

// Lazy initialization of Gemini client to prevent startup crash if unconfigured
let aiClient: GoogleGenAI | null = null;
function getGeminiClient(): GoogleGenAI {
  if (!aiClient) {
    const key = process.env.GEMINI_API_KEY;
    if (!key) {
      throw new Error("GEMINI_API_KEY environment variable is required");
    }
    aiClient = new GoogleGenAI({
      apiKey: key,
      httpOptions: {
        headers: {
          "User-Agent": "aistudio-build",
        },
      },
    });
  }
  return aiClient;
}

// Host health route
app.get("/api/health", (req, res) => {
  res.json({ status: "healthy", timestamp: new Date().toISOString() });
});


// Endpoint to break down any sign dynamically using Structured JSON outputs
app.post("/api/gemini/translate", async (req, res) => {
  try {
    const { phrase } = req.body;
    if (!phrase) {
      res.status(400).json({ error: "Phrase is required." });
      return;
    }

    const ai = getGeminiClient();

    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: `Analyze the mechanics for signing the phrase "${phrase}" and return a complete anatomical breakdown.`,
      config: {
        systemInstruction: "You are a sign language transcription analyst. Provide anatomically precise descriptions for physical fingerspelling, arm gestures, and expressions.",
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          required: ["phrase", "description", "handShape", "armMovement", "facialExpression", "fingerSpelling", "culturalContext"],
          properties: {
            phrase: { type: Type.STRING },
            description: { type: Type.STRING, description: "Concise summary of how this sign is communicated." },
            handShape: { type: Type.STRING, description: "Initial and final fingers/fist states." },
            armMovement: { type: Type.STRING, description: "Detailed trajectory in the signing space (e.g., from chin outwards, circular moving bounds)." },
            facialExpression: { type: Type.STRING, description: "Necessary non-manual signals like brow furrowing, head tilts, mouth shapes, or smiling." },
            fingerSpelling: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
              description: "Array of letters decomposed mapping out the word's manual alphabet sequence."
            },
            culturalContext: { type: Type.STRING, description: "Interesting historical origin or contemporary Deaf convention context." }
          }
        }
      }
    });

    const data = JSON.parse(response.text || "{}");
    res.json(data);
  } catch (error: any) {
    console.error("Translation Breakdown Error:", error);
    res.status(500).json({ error: error.message || "Failed to analyze sign mechanics." });
  }
});

// Setup development and production handlers for express
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on port ${PORT}`);
  });
}

startServer();
