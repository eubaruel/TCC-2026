const path = require("path");
const pythonPath = (environment) => process.platform === "win32"
  ? path.join(__dirname, "backend", environment, "Scripts", "python.exe")
  : path.join(__dirname, "backend", environment, "bin", "python");

// Prepare the environments and dependencies as described in INICIALIZACAO.md.
module.exports = {
  apps: [
    {
      name: "frontend",
      cwd: path.join(__dirname, "frontend"),
      script: "./node_modules/@vue/cli-service/bin/vue-cli-service.js",
      args: "serve"
    },
    {
      name: "sistema-correcao",
      cwd: path.join(__dirname, "backend", "sistema-correcao"),
      script: pythonPath(".venv-leitor"),
      interpreter: "none",
      args: "-m flask --app app --no-debug run --host 127.0.0.1 --port 5000 --no-reload"
    },
    {
      name: "api-principal",
      cwd: path.join(__dirname, "backend"),
      script: pythonPath(".venv-correcao"),
      interpreter: "none",
      args: "app.py"
    }
  ]
};
