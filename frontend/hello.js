const fs = require("fs");
const path = require("path");
const process = require("process");

const args = process.argv.slice(2);
if (args.length !== 1) {
  throw new Error("Missing Environment Type Argument!");
}
const BASE_DIR = path.resolve(__dirname, "..");
const FRONTEND_ENV = path.resolve(BASE_DIR, "frontend", ".en");
const SELECTED_ENV = path.resolve(
  BASE_DIR,
  "environments",
  args[0],
  ".env.frontend"
);

fs.open(FRONTEND_ENV ,"r" , (err , fs )=>{
    if(err){
    fs.writeFile(FRONTEND_ENV , "" , (err)=>{
        if (err ) throw err 
        console.log("create new .env file"); 
    })}
fs.copyFile(SELECTED_ENV , FRONTEND_ENV , (err)=>{
    if(err) throw err; 
    console.log("the file copy content of dev environment")
})
})