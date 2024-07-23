const fs = require("fs");
const path = require("path");
const proces = require("process");

const args = proces.argv.slice(2);
if (args.length !== 1) {
     throw new Error("Missing Environment Type Argument!");
}
const BASE_DIR = path.resolve(__dirname,'..');
const FRONTEND_ENV = path.resolve(BASE_DIR, "frontend", ".env");
const SELECTED_ENV = path.resolve(
  BASE_DIR,
  "environments",
  args[0],
  ".env.frontend"
);
console.log(BASE_DIR);

