import {build} from 'esbuild';
import {copyFile,mkdir} from 'node:fs/promises';
await mkdir('docs',{recursive:true});
await build({entryPoints:['pages/entry.tsx'],bundle:true,format:'iife',jsx:'automatic',minify:true,outfile:'docs/app.js'});
await copyFile('app/globals.css','docs/styles.css');
