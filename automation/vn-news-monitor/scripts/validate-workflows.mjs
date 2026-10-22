#!/usr/bin/env node
// Check every workflow JSON file in a folder (default: workflows/).
// Usage: node scripts/validate-workflows.mjs [dir ...]
// Exit code 0 when no errors. No external packages.
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const dirs = process.argv.slice(2).length ? process.argv.slice(2) : [join(ROOT, 'workflows')];

const SECRET_PATTERNS = [
  { name: 'telegram-token', re: /\d{8,10}:[\w-]{35}/ },
  { name: 'api-key-sk', re: /(^|[^A-Za-z0-9])sk-[A-Za-z0-9_-]{16,}/ },
  { name: 'bearer', re: /Bearer\s+[A-Za-z0-9._~+/-]{8,}/ },
];
const TRIGGER_TYPES = new Set([
  'n8n-nodes-base.scheduleTrigger',
  'n8n-nodes-base.manualTrigger',
  'n8n-nodes-base.errorTrigger',
]);
const NOTE_TYPE = 'n8n-nodes-base.stickyNote';

let errors = 0;
let files = 0;
const fail = (file, msg) => {
  errors++;
  console.log(`ERROR ${file}: ${msg}`);
};

function checkCredentials(file, node) {
  for (const [type, ref] of Object.entries(node.credentials ?? {})) {
    const keys = Object.keys(ref ?? {}).sort().join(',');
    if (keys !== 'id,name' && keys !== 'name') {
      fail(file, `node "${node.name}" credential ${type} must be a reference {id, name}, got keys [${keys}]`);
    }
  }
}

function checkWorkflow(file, wf) {
  if (!Array.isArray(wf.nodes) || typeof wf.connections !== 'object') {
    return fail(file, 'missing nodes[] or connections{}');
  }
  const names = new Map();
  for (const n of wf.nodes) {
    if (names.has(n.name)) fail(file, `duplicate node name "${n.name}"`);
    names.set(n.name, n);
    for (const key of ['type', 'typeVersion', 'position', 'parameters']) {
      if (n[key] === undefined) fail(file, `node "${n.name}" has no ${key}`);
    }
    checkCredentials(file, n);
  }

  const linked = new Set();
  for (const [src, byType] of Object.entries(wf.connections)) {
    if (!names.has(src)) fail(file, `connection from unknown node "${src}"`);
    linked.add(src);
    for (const outputs of Object.values(byType)) {
      for (const targets of outputs ?? []) {
        for (const t of targets ?? []) {
          if (!names.has(t.node)) fail(file, `connection ${src} -> unknown node "${t.node}"`);
          linked.add(t.node);
        }
      }
    }
  }
  for (const n of wf.nodes) {
    if (n.type !== NOTE_TYPE && !linked.has(n.name) && wf.nodes.length > 1) {
      fail(file, `orphan node "${n.name}" (no connections)`);
    }
  }

  // Role comes from the file name: *error-handler* needs an Error Trigger, *setup* runs by hand,
  // every other workflow runs on a schedule and must name an error workflow.
  const types = wf.nodes.map((n) => n.type);
  const isErrorWf = file.includes('error-handler');
  const isSetup = file.includes('setup');
  if (!types.some((t) => TRIGGER_TYPES.has(t))) fail(file, 'no Schedule, Manual or Error Trigger');
  if (isErrorWf && !types.includes('n8n-nodes-base.errorTrigger')) fail(file, 'error workflow without Error Trigger');
  if (!isErrorWf && !isSetup && !types.includes('n8n-nodes-base.scheduleTrigger')) {
    fail(file, 'scheduled workflow without Schedule Trigger');
  }
  if (wf.settings?.timezone !== 'Asia/Ho_Chi_Minh') {
    fail(file, `settings.timezone is "${wf.settings?.timezone}", expected "Asia/Ho_Chi_Minh"`);
  }
  if (!isErrorWf && !isSetup && !wf.settings?.errorWorkflow) fail(file, 'settings.errorWorkflow is missing');
  if (wf.active === true) fail(file, 'workflow is active in JSON; keep active=false');
}

for (const dir of dirs) {
  for (const name of readdirSync(dir).sort()) {
    const path = join(dir, name);
    if (!name.endsWith('.json') || !statSync(path).isFile()) continue;
    files++;
    const raw = readFileSync(path, 'utf8');
    for (const p of SECRET_PATTERNS) {
      if (p.re.test(raw)) fail(name, `text looks like a secret (${p.name})`);
    }
    let wf;
    try {
      wf = JSON.parse(raw);
    } catch (e) {
      fail(name, `invalid JSON: ${e.message}`);
      continue;
    }
    const before = errors;
    checkWorkflow(name, wf);
    if (errors === before) console.log(`OK    ${name} (${wf.nodes.length} nodes)`);
  }
}
console.log(`\n${files} file(s), ${errors} error(s)`);
process.exit(errors === 0 && files > 0 ? 0 : 1);
