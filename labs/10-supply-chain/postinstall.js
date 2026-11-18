const fs = require("node:fs");
const path = require("node:path");

const marker = path.join(process.cwd(), "postinstall-ran.txt");
fs.writeFileSync(marker, "postinstall executed inside the temporary lab directory\n");
console.log("postinstall: wrote marker file");
