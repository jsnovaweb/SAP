import { spawn } from "child_process";

console.log("Starting Streamlit Application...");

// Spawn the Streamlit process
// We use shell: true to ensure the command is found in the path
const streamlit = spawn("streamlit", ["run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0"], {
  stdio: "inherit",
  shell: true
});

streamlit.on("error", (err) => {
  console.error("Failed to start Streamlit:", err);
});

streamlit.on("close", (code) => {
  console.log(`Streamlit process exited with code ${code}`);
  process.exit(code ?? 0);
});

// Handle termination signals to cleanup the child process
const cleanup = () => {
  console.log("Stopping Streamlit...");
  streamlit.kill();
  process.exit(0);
};

process.on("SIGTERM", cleanup);
process.on("SIGINT", cleanup);
