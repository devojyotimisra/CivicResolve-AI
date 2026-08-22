import fs from 'fs';
import path from 'path';
import strip from 'strip-comments';

function processDirectory(dir) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      processDirectory(fullPath);
    } else if (file.endsWith('.js') || file.endsWith('.jsx')) {
      if (file.includes('eslint.config.js') || file.includes('vite.config.js')) continue;
      console.log(`Processing ${fullPath}`);
      const content = fs.readFileSync(fullPath, 'utf8');
      const stripped = strip(content);
      fs.writeFileSync(fullPath, stripped, 'utf8');
    }
  }
}

const frontendSrc = path.join(process.cwd(), 'src');
processDirectory(frontendSrc);
