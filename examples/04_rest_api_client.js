/**
 * Example 04: Node.js / JavaScript Client for Ziskare AI REST API
 * 
 * To run this example:
 * 1. Start the server: `ziskare-ai --server 5005`
 * 2. In another terminal run: `node 04_rest_api_client.js`
 */

async function queryZiskareAI(prompt) {
  try {
    const response = await fetch('http://127.0.0.1:5005/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt })
    });

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const data = await response.json();
    console.log("Q:", prompt);
    console.log("Ziskare AI:", data.answer);
    console.log(`⏱️ Speed: ${data.speed} tokens/sec (${data.time_taken}s)\n`);
  } catch (err) {
    console.error("Could not connect to Ziskare AI server. Is it running? (ziskare-ai --server 5005)");
  }
}

async function main() {
  console.log("--- Querying Ziskare AI REST API ---\n");
  await queryZiskareAI("What is an API gateway?");
  await queryZiskareAI("Explain event loop in Node.js in 15 words.");
}

main();
