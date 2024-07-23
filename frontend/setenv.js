// This script replaces the values in .env with those in the environment directory depending on the argument given
// For example: To run with 'stage' environment variables, call 'setenv.py stage'
/* eslint-disable */
const fs = require("fs");
const path = require("path");
const proces = require("process");

const args = proces.argv.slice(2);
if (args.length !== 1) {
  throw new Error("Missing Environment Type Argument!");
}
const BASE_DIR = path.resolve(__dirname, "..");
const FRONTEND_ENV = path.resolve(BASE_DIR, "frontend", ".env");
const SELECTED_ENV = path.resolve(
  BASE_DIR,
  "environments",
  args[0],
  ".env.frontend"
);

fs.open(FRONTEND_ENV, "r", function (err, fd) {
  if (err) {
    fs.writeFile(FRONTEND_ENV, "", function (err) {
      if (err) throw err;
      console.log("The file was saved!");
    });
  }
  fs.copyFile(SELECTED_ENV, FRONTEND_ENV, (err) => {
    if (err) throw err;
    console.log("Frontend environment has been set to", args[0]);
  });
});
