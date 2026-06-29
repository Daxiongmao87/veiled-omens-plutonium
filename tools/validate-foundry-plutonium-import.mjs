#!/usr/bin/env node

import fs from 'node:fs/promises';
import fsSync from 'node:fs';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import net from 'node:net';

const requirePlaywright = async () => {
	try {
		return await import('playwright-core');
	} catch (error) {
		console.error(`PLAYWRIGHT_CORE_IMPORT_ERROR: ${error.message}`);
		return null;
	}
};

const ROOT_DIR = process.cwd();
const PACKAGE_REL = process.env.PACKAGE_JSON || 'collection/Patrick Richardson; Veiled Omens Campaign Setting.json';
const PACKAGE_PATH = path.resolve(ROOT_DIR, PACKAGE_REL);
const WORLD_NAME = process.env.FOUNDRY_WORLD || 'veiled-omens-import';
const APP_DIR = process.env.FOUNDRY_APP_DIR ? path.resolve(process.env.FOUNDRY_APP_DIR) : null;
const TEMPLATE_DIR = process.env.FOUNDRY_DATA_DIR ? path.resolve(process.env.FOUNDRY_DATA_DIR) : null;
const FOUNDRY_PORT = Number(process.env.FOUNDRY_PORT || 30000);
const STATIC_PORT_ENV = process.env.FOUNDRY_STATIC_PORT;
const REPORT_PATH = process.env.FOUNDRY_IMPORT_REPORT_PATH || path.resolve(ROOT_DIR, 'tmp', 'foundry-plutonium-import-result.json');
const FOUNDRY_NODE = process.env.FOUNDRY_NODE || process.execPath;
const CHROMIUM_PATH = process.env.CHROMIUM_EXECUTABLE_PATH;
const SOURCE_ID = process.env.VO_SOURCE_ID || 'VeiledOmens';
const FOUNDRY_USER_ID = (process.env.FOUNDRY_USER_ID || '').trim();
const FOUNDRY_USER_PASSWORD = process.env.FOUNDRY_USER_PASSWORD || '';
const HEADLESS = process.env.FOUNDRY_HEADLESS ? process.env.FOUNDRY_HEADLESS !== 'false' : true;
const FOUNDRY_NO_CANVAS = process.env.FOUNDRY_NO_CANVAS ? process.env.FOUNDRY_NO_CANVAS !== 'false' : true;
const FOUNDRY_IMPORT_STEP_TIMEOUT_MS = (() => {
	const parsed = Number.parseInt(process.env.FOUNDRY_IMPORT_STEP_TIMEOUT_MS || '', 10);
	if (Number.isFinite(parsed) && parsed > 0) return parsed;
	return 300000;
})();
const ARGS = new Set(process.argv.slice(2));
const PLAYWRIGHT_VIEWPORT = {
	width: 1440,
	height: 900,
};

const IMPORT_LEVELS = Array.from(new Set((process.env.FOUNDRY_IMPORT_LEVELS || '1,2,3')
	.split(',')
	.map((value) => Number(value.trim()))
	.filter((value) => Number.isFinite(value) && value > 0)
	.map((value) => Math.trunc(value))))
	.sort((a, b) => a - b);

if (IMPORT_LEVELS.length === 0) {
	IMPORT_LEVELS.push(1, 2, 3);
}

const PASS = [];
const FAIL = [];

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const ensure = async (value, message) => {
	if (!value) {
		FAIL.push(message);
		console.log(`BLOCKER: ${message}`);
		return false;
	}

	PASS.push(message);
	console.log(`PASS: ${message}`);
	return true;
};

const getFileJson = async (filePath) => {
	const raw = await fs.readFile(filePath, 'utf8');
	return JSON.parse(raw);
};

const findPackageFile = async () => {
	if (!(await fs.access(PACKAGE_PATH).then(() => true).catch(() => false))) {
		return false;
	}
	try {
		return await getFileJson(PACKAGE_PATH);
	} catch (error) {
		FAIL.push(`Package file is not valid JSON at ${PACKAGE_PATH}: ${error.message}`);
		return false;
	}
};

const checkFile = async (target) => {
	try {
		await fs.access(target);
		return true;
	} catch {
		return false;
	}
};

const fileExists = (target) => fsSync.existsSync(target);

const readJsonValue = async (filePath, prop = 'version') => {
	try {
		const raw = await getFileJson(filePath);
		return raw?.[prop] ?? 'n/a';
	} catch {
		return 'n/a';
	}
};

const getWorldDir = (dataDir) => path.join(dataDir, 'Data', 'worlds', WORLD_NAME);

const getFoundryLandingState = async (page) => page.evaluate(() => {
	const select = document.querySelector('select[name="userid"]');
	const joinButton = document.querySelector('button[type="submit"]');
	const joinForm = document.querySelector('form[action*="/join"]') || document.querySelector('form[data-route="join"]');
	return {
		pathname: window.location.pathname,
		isJoinPath: window.location.pathname.startsWith('/join'),
		gameReady: !!(window.game && window.game.ready),
		hasJoinForm: !!select || !!joinForm,
		hasJoinSelect: !!select,
		hasEnabledJoinUsers: !!select && Array.from(select.options).some((option) => !option.disabled && option.value),
		joinUserCount: !!select ? Array.from(select.options).filter((option) => !option.disabled && option.value).length : 0,
		passwordVisible: !!document.querySelector('input[type="password"], input[name="password"]'),
		submitButtonVisible: !!joinButton,
	};
});

const waitForFoundryJoinReadiness = async (page, timeoutMs = 120000) => {
	const startedAt = Date.now();
	const checkIntervalMs = 250;
	let state = await getFoundryLandingState(page);

	while (!state.gameReady && !state.hasJoinSelect && Date.now() - startedAt < timeoutMs) {
		await delay(checkIntervalMs);
		state = await getFoundryLandingState(page);
	}

	return state;
};

const performFoundryJoin = async (page, state, report) => {
	await page.waitForSelector('select[name="userid"]', {timeout: 120000}).catch(() => {
		throw new Error('Join user selector [name="userid"] did not appear before evaluating available users.');
	});

	const joinDecision = await page.evaluate((requestedUserId) => {
		const select = document.querySelector('select[name="userid"]');
		if (!select) {
			return {
				ok: false,
				reason: 'Join user selector [name="userid"] is not present on the page.',
				selectedUserId: null,
				userCount: 0,
			};
		}

		const enabledOptions = Array.from(select.options).filter((option) => !option.disabled && option.value);
		if (!enabledOptions.length) {
			return {
				ok: false,
				reason: 'No enabled users are available on the Foundry join form.',
				selectedUserId: null,
				userCount: 0,
			};
		}

		const requested = requestedUserId ? requestedUserId.trim() : '';
		const normalizedRequest = requested.toLowerCase();
		const requestedMatch = requested ? enabledOptions.find((option) => {
			const value = (option.value || '').toLowerCase();
			const label = (option.text || '').toLowerCase();
			return value === requested || label === normalizedRequest;
		}) : null;

		const selected = requestedMatch || enabledOptions[0];
		select.value = selected.value;
		return {
			ok: true,
			selectedUserId: selected.value,
			selectedLabel: selected.text,
			requestedMatched: !!requestedMatch,
			userCount: enabledOptions.length,
		};
	}, FOUNDRY_USER_ID);

	if (!joinDecision.ok) {
		await page.evaluate((reason) => { window.__foundryJoinState = reason; }, joinDecision.reason);
		throw new Error(joinDecision.reason);
	}

	const requestedMatched = joinDecision.requestedMatched;
	if (FOUNDRY_USER_ID && !requestedMatched) {
		throw new Error(`FOUNDRY_USER_ID "${FOUNDRY_USER_ID}" is not available on the join form.`);
	}

	await page.selectOption('select[name="userid"]', joinDecision.selectedUserId).catch((error) => {
		throw new Error(`Could not set join user selection: ${error?.message || String(error)}`);
	});

	const passwordSelector = 'input[type="password"], input[name="password"]';
	const passwordInput = await page.$(passwordSelector);
	if (passwordInput) {
		try {
			await passwordInput.fill(FOUNDRY_USER_PASSWORD);
		} catch (error) {
			throw new Error(`Failed to populate Foundry join password field: ${error?.message || String(error)}`);
		}
	}

	const submitButton = page.locator('form[action*="/join"] button[type="submit"], form button[type="submit"], button[type="submit"]').first();
	const hasSubmitButton = await submitButton.count();

	try {
		if (hasSubmitButton) {
			await Promise.all([
				page.waitForURL(/\/game(?:\/|$|[?#])/i, {timeout: 120000}),
				submitButton.click(),
			]);
		} else if (passwordInput) {
			await Promise.all([
				page.waitForURL(/\/game(?:\/|$|[?#])/i, {timeout: 120000}),
				passwordInput.press('Enter'),
			]);
		} else {
			throw new Error('Join form submit control is not available.');
		}
	} catch (error) {
		throw new Error(`Failed to submit Foundry join form: ${error?.message || String(error)}`);
	}

	report.login = {
		...state,
		attempted: true,
		requestedUserId: FOUNDRY_USER_ID || null,
		requestedMatched,
		selectedUserId: joinDecision.selectedUserId,
		selectedLabel: joinDecision.selectedLabel,
		userCount: joinDecision.userCount,
		passwordProvided: Boolean(FOUNDRY_USER_PASSWORD),
		submittedViaJoinUI: true,
	};
	return true;
};

const isPortFree = (port) => new Promise((resolve) => {
	const server = net.createServer();
	server.once('error', () => resolve(false));
	server.once('listening', () => {
		server.close(() => resolve(true));
	});
	server.listen(port, '127.0.0.1');
});

const chooseFreePort = async (preferred) => {
	const start = Number(preferred || 0);
	if (!Number.isFinite(start) || start <= 0) {
		return 0;
	}

	for (let port = start; port < start + 40; port++) {
		if (await isPortFree(port)) return port;
	}

	return 0;
};

const copyTemplate = async (srcDir, targetDir) => {
	await fs.mkdir(targetDir, {recursive: true});
	await fs.cp(srcDir, targetDir, {recursive: true});
};

const ensureWorldDirFromTemplate = async (templateDataDir, tempDataDir) => {
	const templateWorldDir = path.join(templateDataDir, 'Data', 'worlds', WORLD_NAME);
	const tempWorldDir = path.join(tempDataDir, 'Data', 'worlds', WORLD_NAME);
	await fs.mkdir(path.dirname(tempWorldDir), {recursive: true});
	await copyTemplate(templateWorldDir, tempWorldDir);
	return {
		mode: 'copied',
		source: templateWorldDir,
		target: tempWorldDir,
	};
};

const linkTemplateDirectory = async (templateDataDir, tempDataDir, relPath, {
	required = true,
	sourceOnly = false,
} = {}) => {
	const sourcePath = path.join(templateDataDir, relPath);
	const targetPath = path.join(tempDataDir, relPath);
	const exists = await checkFile(sourcePath);
	if (!exists) {
		if (required) {
			throw new Error(`Template data directory missing for required symlink: ${sourcePath}`);
		}
		return {
			used: 'missing',
			required,
			source: sourcePath,
			target: targetPath,
			reason: 'Not present in template directory',
		};
	}

	await fs.mkdir(path.dirname(targetPath), {recursive: true});

	if (sourceOnly) {
		return {
			used: 'not-linked',
			required,
			source: sourcePath,
			target: targetPath,
			reason: 'Template-only strategy disabled',
		};
	}

	try {
		await fs.symlink(sourcePath, targetPath, 'dir');
		return {
			used: 'symlink',
			required,
			source: sourcePath,
			target: targetPath,
			reason: 'Linked to template directory',
		};
	} catch (error) {
		throw new Error(`Failed to symlink ${sourcePath} -> ${targetPath}: ${error.message}`);
	}
};

const prepareRunData = async (templateDataDir, tempDataDir) => {
	const configSource = path.join(templateDataDir, 'Config');
	const configTarget = path.join(tempDataDir, 'Config');
	const worldsSource = path.join(templateDataDir, 'Data', 'worlds', WORLD_NAME);
	const worldsTarget = path.join(tempDataDir, 'Data', 'worlds', WORLD_NAME);

	await copyTemplate(configSource, configTarget);
	const worldLayout = await ensureWorldDirFromTemplate(templateDataDir, tempDataDir);
	const modulesLayout = await linkTemplateDirectory(templateDataDir, tempDataDir, path.join('Data', 'modules'));
	const systemsLayout = await linkTemplateDirectory(templateDataDir, tempDataDir, path.join('Data', 'systems'));
	const assetsLayout = await linkTemplateDirectory(templateDataDir, tempDataDir, path.join('Data', 'assets'), {required: false});

	return {
		config: {
			used: 'copied',
			source: configSource,
			target: configTarget,
		},
		worlds: {
			...worldLayout,
		},
		modules: modulesLayout,
		systems: systemsLayout,
		assets: assetsLayout,
		exists: {
			configSource: await checkFile(configSource),
			worldSourceExists: await checkFile(worldsSource),
			modulesSourceExists: await checkFile(path.join(templateDataDir, 'Data', 'modules')),
			systemsSourceExists: await checkFile(path.join(templateDataDir, 'Data', 'systems')),
			assetsSourceExists: await checkFile(path.join(templateDataDir, 'Data', 'assets')),
		},
		worldsTarget: worldsTarget,
	};
};

const startStaticServer = async (rootDir, requestedPort) => {
	const server = createServer((req, res) => {
		res.setHeader('Access-Control-Allow-Origin', '*');
		res.setHeader('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS');
		res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

		if (req.method === 'OPTIONS') {
			res.writeHead(204);
			res.end();
			return;
		}

		const reqUrl = new URL(req.url, `http://127.0.0.1:${requestedPort || 0}`);
		const relPath = decodeURIComponent(reqUrl.pathname.replace(/^\/+/, ''));
		const absPath = path.resolve(rootDir, relPath || '.');

		if (!absPath.startsWith(rootDir)) {
			res.writeHead(403);
			res.end('Forbidden');
			return;
		}

		fsSync.promises.stat(absPath).then((stat) => {
			if (stat.isDirectory()) {
				res.writeHead(404);
				res.end('Directory listing not supported');
				return;
			}
			fsSync.createReadStream(absPath)
				.on('error', () => {
					res.writeHead(404);
					res.end('Not found');
				})
				.pipe(res);
		}).catch(() => {
			res.writeHead(404);
			res.end('Not found');
		});
	});

	const listenPort = await new Promise((resolve, reject) => {
		server.once('error', reject);
		server.listen(requestedPort || 0, '127.0.0.1', () => {
			resolve(server.address().port);
		});
	});

	return {server, port: listenPort};
};

const waitForFoundry = async (port) => {
	const url = `http://127.0.0.1:${port}`;
	const timeoutAt = Date.now() + 120000;
	let lastError;

	while (Date.now() < timeoutAt) {
		try {
			const response = await fetch(url);
			if (response.ok || response.status === 301 || response.status === 302) {
				return true;
			}
			lastError = `HTTP ${response.status}`;
		} catch (error) {
			lastError = error.message;
		}

		await delay(700);
	}

	FAIL.push(`Foundry did not start on port ${port} in time: ${lastError || 'timeout'}`);
	return false;
};

const preflight = async () => {
	let valid = true;

	if (!APP_DIR) {
		valid = await ensure(false, 'FOUNDRY_APP_DIR must be set in environment for preflight') && valid;
	} else {
		valid = await ensure(await checkFile(APP_DIR), `Foundry app dir exists: ${APP_DIR}`) && valid;
		valid = await ensure(await checkFile(path.join(APP_DIR, 'package.json')), `Foundry app package.json exists: ${path.join(APP_DIR, 'package.json')}`) && valid;
		valid = await ensure(await checkFile(path.join(APP_DIR, 'main.js')), `Foundry app main.js exists: ${path.join(APP_DIR, 'main.js')}`) && valid;
		console.log(`INFO: Foundry app version ${await readJsonValue(path.join(APP_DIR, 'package.json'))}`);
	}

	if (!TEMPLATE_DIR) {
		valid = await ensure(false, 'FOUNDRY_DATA_DIR must be set in environment for preflight') && valid;
	} else {
		valid = await ensure(await checkFile(TEMPLATE_DIR), `Foundry data template exists: ${TEMPLATE_DIR}`) && valid;
		const systemPath = path.join(TEMPLATE_DIR, 'Data', 'systems', 'dnd5e', 'system.json');
		const plutoniumPath = path.join(TEMPLATE_DIR, 'Data', 'modules', 'plutonium', 'module.json');
		const libWrapperPath = path.join(TEMPLATE_DIR, 'Data', 'modules', 'lib-wrapper', 'module.json');
		valid = await ensure(await checkFile(systemPath), `Foundry data template has dnd5e module at ${systemPath}`) && valid;
		valid = await ensure(await checkFile(plutoniumPath), `Foundry data template has plutonium module at ${plutoniumPath}`) && valid;
		valid = await ensure(await checkFile(libWrapperPath), `Foundry data template has lib-wrapper module at ${libWrapperPath}`) && valid;
		valid = await ensure(await checkFile(getWorldDir(TEMPLATE_DIR)), `Foundry world exists in template: ${WORLD_NAME}`) && valid;
		console.log(`INFO: dnd5e version ${await readJsonValue(systemPath)}`);
		console.log(`INFO: Plutonium version ${await readJsonValue(plutoniumPath)}`);
		console.log(`INFO: lib-wrapper version ${await readJsonValue(libWrapperPath)}`);
	}

	const foundryPlaywright = await requirePlaywright();
	if (!foundryPlaywright) {
		valid = await ensure(false, 'Cannot resolve playwright-core module. Run `npm install` in this repo before running harness.') && valid;
	} else {
		console.log('PASS: playwright-core resolved');
	}

	if (CHROMIUM_PATH) {
		valid = await ensure(fileExists(CHROMIUM_PATH), `Chromium executable exists at ${CHROMIUM_PATH}`) && valid;
	} else {
		valid = await ensure(false, 'CHROMIUM_EXECUTABLE_PATH must be set when using playwright-core (playwright-core cannot download browsers).') && valid;
	}

	const packageData = await findPackageFile();
	if (!packageData) {
		valid = await ensure(false, `Package file exists and is valid JSON at ${PACKAGE_PATH}`) && valid;
	} else {
		const hasArray = ['race', 'class', 'subclass', 'spell', 'background', 'feat', 'item', 'optionalfeature']
			.some((prop) => Array.isArray(packageData[prop]) && packageData[prop].length > 0);
		valid = await ensure(hasArray, `Package file has player-facing arrays at ${PACKAGE_PATH}`) && valid;
		console.log(`INFO: Package file ${PACKAGE_PATH} has player-facing arrays=${hasArray ? 'present' : 'missing'}`);
	}

	console.log(`INFO: Foundry app dir = ${APP_DIR}`);
	console.log(`INFO: Foundry data dir = ${TEMPLATE_DIR}`);
	console.log(`INFO: Package file = ${PACKAGE_PATH}`);
	console.log(`INFO: Foundry import levels = ${IMPORT_LEVELS.join(',')}`);

	if (!valid) {
		console.log('BLOCKER: Preflight failed.');
		process.exit(1);
	}

	console.log('PASS: Preflight complete');
};

const buildPlaywrightImportPlan = async () => {
	const packageData = await findPackageFile();
	if (!packageData) throw new Error(`Package file invalid: ${PACKAGE_PATH}`);

	const races = (packageData.race || []).map((entry) => ({name: entry.name, source: entry.source}));
	const classes = (packageData.class || []).map((entry) => ({name: entry.name, source: entry.source}));
	const subclasses = (packageData.subclass || []).map((entry) => ({
		name: entry.name,
		source: entry.source,
		className: entry.className,
		classSource: entry.classSource,
	}));

	return {
		sourceId: SOURCE_ID,
		levels: IMPORT_LEVELS,
		races,
		classes,
		subclasses,
	};
};

const buildResultBase = async (packageData) => {
	return {
		execution: {
			foundryAppDir: APP_DIR,
			foundryDataTemplate: TEMPLATE_DIR,
			foundryPackageFile: PACKAGE_PATH,
			importStepTimeoutMs: FOUNDRY_IMPORT_STEP_TIMEOUT_MS,
		},
		versions: {
			foundryApp: await readJsonValue(path.join(APP_DIR || '', 'package.json')),
			dnd5e: await readJsonValue(path.join(TEMPLATE_DIR || '', 'Data', 'systems', 'dnd5e', 'system.json')),
			plutonium: await readJsonValue(path.join(TEMPLATE_DIR || '', 'Data', 'modules', 'plutonium', 'module.json')),
		},
		packageSource: SOURCE_ID,
		sourceLoaded: null,
		storage: {},
		imported: [],
		failures: [],
		serverLogs: [],
		browserLogs: [],
	};
};

const normalizeReport = (entry) => {
	if (!entry || typeof entry !== 'object') return entry;
	return {
		...entry,
		actorId: entry.actorId || entry.id,
		itemSummary: (entry.items || []).map((it) => ({
			name: it.name,
			type: it.type,
			flags: it.flags || {},
		})),
	};
};

const runImport = async (plan) => {
	const packageData = await findPackageFile();
	if (!packageData) throw new Error(`Package file invalid: ${PACKAGE_PATH}`);
	const report = await buildResultBase(packageData);
	report.packageVersion = packageData?._meta?.sources?.[0]?.version || 'n/a';

	const tempRoot = path.resolve(ROOT_DIR, 'tmp', `foundry-plutonium-import-${Date.now()}`);
	const staticRoot = ROOT_DIR;
	const logs = {
		foundry: [],
		browser: [],
	};
	let foundryProcess = null;
	let staticServer = null;
	let browser = null;
	let page = null;

	const cleanup = async (exitCode = 0, blocker = null) => {
		if (page) {
			try {
				await page.close();
			} catch {}
		}
		if (browser) {
			try {
				await browser.close();
			} catch {}
		}
		if (foundryProcess && !foundryProcess.killed) {
			try {
				foundryProcess.kill('SIGTERM');
				await delay(1000);
				if (!foundryProcess.killed) {
					foundryProcess.kill('SIGKILL');
				}
			} catch {}
		}
		if (staticServer) {
			try {
				await new Promise((resolve) => staticServer.close(resolve));
			} catch {}
		}
		try {
			await fs.rm(tempRoot, {recursive: true, force: true});
		} catch {}

		report.serverLogs = logs.foundry;
		report.browserLogs = logs.browser;
		report.timestamp = new Date().toISOString();
		report.status = exitCode === 0 ? 'passed' : 'blocked';
		if (blocker) {
			report.blocker = blocker;
		}

		await fs.mkdir(path.dirname(REPORT_PATH), {recursive: true});
		await fs.writeFile(REPORT_PATH, JSON.stringify(report, null, 2), 'utf8');
		console.log(`INFO: Wrote report ${REPORT_PATH}`);
		if (blocker) {
			console.log(`BLOCKER: ${blocker}`);
		}
		process.exit(exitCode);
	};

		try {
			if (!APP_DIR || !TEMPLATE_DIR) {
				throw new Error('FOUNDRY_APP_DIR and FOUNDRY_DATA_DIR are required. Run with --preflight first and set both environment values.');
			}

			report.storage = await prepareRunData(TEMPLATE_DIR, tempRoot);
		const worldDir = getWorldDir(tempRoot);
			await fs.mkdir(worldDir, {recursive: true});
			report.templatedDataPath = tempRoot;

		const staticPort = STATIC_PORT_ENV ? Number(STATIC_PORT_ENV) : 0;
		const {server, port: staticPortActual} = await startStaticServer(staticRoot, staticPort);
		staticServer = server;
		report.staticServerPort = staticPortActual;

		const foundryPort = await chooseFreePort(FOUNDRY_PORT) || FOUNDRY_PORT;
		report.foundryPort = foundryPort;

		const foundryLogPrefix = `Foundry(${foundryPort})`;
		foundryProcess = spawn(
			FOUNDRY_NODE,
			[
				path.join(APP_DIR, 'main.js'),
				`--dataPath=${tempRoot}`,
				`--port=${foundryPort}`,
				`--world=${WORLD_NAME}`,
				'--noupdate',
			],
			{
				env: {...process.env},
				detached: false,
				stdio: ['ignore', 'pipe', 'pipe'],
			},
		);

		foundryProcess.stdout.on('data', (chunk) => {
			const line = chunk.toString().trim();
			if (line) {
				logs.foundry.push(`${foundryLogPrefix}:${line}`);
			}
		});
		foundryProcess.stderr.on('data', (chunk) => {
			const line = chunk.toString().trim();
			if (line) {
				logs.foundry.push(`${foundryLogPrefix} ERR:${line}`);
			}
		});

		if (!await waitForFoundry(foundryPort)) {
			await cleanup(1, `Foundry failed to start on port ${foundryPort}`);
		}

		const playwright = await requirePlaywright();
		if (!playwright) {
			await cleanup(1, 'playwright-core is unavailable. Run `npm install` before running this harness.');
		}

		const launchOpts = {headless: HEADLESS};
		if (CHROMIUM_PATH) {
			launchOpts.executablePath = CHROMIUM_PATH;
		}
		launchOpts.args = ['--window-size=1440,900'];

		browser = await playwright.chromium.launch(launchOpts);
		const context = await browser.newContext({viewport: PLAYWRIGHT_VIEWPORT});
		report.clientSettings = {
			noCanvas: FOUNDRY_NO_CANVAS,
		};
		await context.addInitScript((noCanvas) => {
			if (!noCanvas) return;
			try {
				window.localStorage.setItem('core.noCanvas', JSON.stringify(true));
			} catch {
				// Foundry will report readiness failures if localStorage is unavailable.
			}
		}, FOUNDRY_NO_CANVAS);
		page = await context.newPage();
		let pageError = null;
		page.on('console', (msg) => {
			logs.browser.push(`console:${msg.type()}:${msg.text()}`);
		});
		page.on('pageerror', (error) => {
			pageError = error?.message || String(error);
			logs.browser.push(`pageerror:${error?.message || String(error)}`);
		});
		page.on('requestfailed', (request) => {
			logs.browser.push(`requestfailed:${request.resourceType()}:${request.url()}:${request.failure()?.errorText || 'unknown'}`);
		});
		page.on('response', (response) => {
			if (response.status() >= 400) {
				logs.browser.push(`response:${response.status()}:${response.url()}`);
			}
		});

		await page.goto(`http://127.0.0.1:${foundryPort}/`, {waitUntil: 'domcontentloaded', timeout: 120000});
		const landingState = await waitForFoundryJoinReadiness(page, 120000);

		if (!landingState.gameReady && !landingState.hasJoinSelect) {
			await cleanup(1, 'Join user selector [name="userid"] did not appear and window.game.ready was never reported after page load.');
		}

		report.login = {
			attempted: false,
			requestedUserId: FOUNDRY_USER_ID || null,
			passwordProvided: Boolean(FOUNDRY_USER_PASSWORD),
			landingPagePath: landingState.pathname,
		};

		if (landingState.gameReady) {
			report.login.status = 'skipped-game-already-ready';
		} else if (landingState.hasJoinForm || landingState.isJoinPath) {
			try {
				await performFoundryJoin(page, landingState, report);
			} catch (error) {
				await cleanup(1, `Join form submission failed: ${error.message}`);
			}
		} else {
			await cleanup(1, `Expected join flow or ready state at ${landingState.pathname}, but neither was detected.`);
		}

		if (pageError) {
			await cleanup(1, `Browser page error before ready: ${pageError}`);
		}

		try {
			await page.waitForFunction(() => window.game && window.game.ready, undefined, {timeout: 120000});
		} catch (error) {
			await cleanup(1, `window.game.ready did not become true after join attempt: ${error.message}`);
		}

		if (!landingState.gameReady && report.login.attempted) {
			const finalPath = await page.evaluate(() => window.location.pathname);
			if (!finalPath.startsWith('/game')) {
				await cleanup(1, `Join flow did not land on /game route. Current path: ${finalPath}`);
			}
		}

		if (pageError) {
			await cleanup(1, `Browser page error during join/ready flow: ${pageError}`);
		}

		const readyState = await page.evaluate(() => {
			return {
				gameReady: !!(window.game && window.game.ready),
				pathname: window.location.pathname,
			};
		});
		if (!readyState.gameReady) {
			await cleanup(1, `window.game.ready did not become true. Last path: ${readyState.pathname}`);
		}

		const bootInfo = await page.evaluate(() => {
			const systemId = game?.system?.id;
			const systemVersion = game?.system?.version ?? null;
			const systemTitle = game?.system?.title ?? null;
			const plutonium = game.modules.get('plutonium');
			const libWrapper = game.modules.get('lib-wrapper');
			return {
				systemId,
				systemVersion,
				systemTitle,
				dnd5e: systemId === 'dnd5e',
				plutonium: !!plutonium?.active,
				libWrapper: !!libWrapper?.active,
				world: game.world?.id,
			};
		});
		report.boot = bootInfo;

		if (!bootInfo.dnd5e || !bootInfo.plutonium || !bootInfo.libWrapper) {
			await cleanup(1, 'Required dnd5e system and required modules are not active in the world.');
		}
		if (bootInfo.world !== WORLD_NAME) {
			await cleanup(1, `Loaded world '${bootInfo.world || 'unknown'}' is not expected '${WORLD_NAME}'.`);
		}

		report.boot = bootInfo;

		const safePackagePath = PACKAGE_REL.split('/').map((segment) => encodeURIComponent(segment)).join('/');
		report.packageUrl = `http://127.0.0.1:${staticPortActual}/${safePackagePath}`;
		report.sourceLoaded = await page.evaluate(async ({url, sourceId}) => {
			await window.BrewUtil2.pAddBrewFromUrl(url);
			await window.BrewUtil2.pGetBrewProcessed();
			return window.BrewUtil2.hasSourceJson(sourceId);
		}, {url: report.packageUrl, sourceId: SOURCE_ID});

		if (!report.sourceLoaded) {
			await cleanup(1, `Failed to load source ${SOURCE_ID} from ${report.packageUrl}`);
		}

		report.importPlan = {
			sourceId: plan.sourceId || SOURCE_ID,
			levels: plan.levels || IMPORT_LEVELS,
			levelsLabel: (plan.levels || IMPORT_LEVELS).join(','),
			races: plan.races || [],
			classes: plan.classes || [],
			subclasses: plan.subclasses || [],
		};

		const importResult = await page.evaluate(async ({plan, levels, importStepTimeoutMs}) => {
			const summaries = [];
			const failures = [];
			const plutoniumModuleApi = game.modules.get('plutonium')?.api;
			const importTrace = {
				events: [],
				maxEvents: 500,
				nextId: 1,
				startedAt: Date.now(),
			};
			const promptAutomation = {
				enabled: true,
				events: [],
				handled: {},
				maxEvents: 200,
				startedAt: Date.now(),
			};

			const normText = (value) => (value || '')
				.toString()
				.replace(/\s+/g, ' ')
				.trim()
				.toLowerCase();

			const isVisible = (element) => {
				try {
					if (!element || !(element instanceof Element)) return false;
					const style = window.getComputedStyle(element);
					const rect = element.getBoundingClientRect();
					return style.display !== 'none'
						&& style.visibility !== 'hidden'
						&& Number(style.opacity) > 0
						&& rect.width > 1
						&& rect.height > 1;
				} catch {
					return false;
				}
			};

			const recordPromptEvent = (payload) => {
				promptAutomation.events.push({
					ts: Date.now(),
					...payload,
				});
				if (promptAutomation.events.length > promptAutomation.maxEvents) {
					promptAutomation.events.shift();
				}
			};

			const recordImportTrace = (payload) => {
				importTrace.events.push({
					ts: Date.now(),
					...payload,
				});
				if (importTrace.events.length > importTrace.maxEvents) {
					importTrace.events.shift();
				}
			};

			const summarizeTraceArg = (arg) => {
				if (arg == null) return arg;
				if (Array.isArray(arg)) {
					return {
						type: 'array',
						length: arg.length,
						first: summarizeTraceArg(arg[0]),
					};
				}
				if (typeof arg !== 'object') return {
					type: typeof arg,
					value: String(arg).slice(0, 120),
				};
				const out = {
					type: arg.constructor?.name || 'object',
				};
				for (const prop of ['name', 'source', '__prop', 'id', '_id', 'type']) {
					if (arg[prop] != null) out[prop] = arg[prop];
				}
				if (arg.actor) out.actor = summarizeTraceArg(arg.actor);
				return out;
			};

			const getImportTraceDiagnostics = () => ({
				eventCount: importTrace.events.length,
				latestEvents: importTrace.events.slice(-40),
				events: importTrace.events,
			});

			const wrapImporterAsyncMethod = (target, methodName, label) => {
				const original = target?.[methodName];
				if (typeof original !== 'function') {
					recordImportTrace({
						label: 'method-unavailable',
						methodName,
						traceLabel: label,
						targetType: target?.constructor?.name || null,
					});
					return;
				}

				target[methodName] = async function (...args) {
					const traceId = importTrace.nextId++;
					const startedAt = Date.now();
					recordImportTrace({
						label: 'start',
						traceId,
						methodName,
						traceLabel: label,
						targetType: this?.constructor?.name || null,
						args: args.map(summarizeTraceArg),
					});
					try {
						const out = await original.apply(this, args);
						recordImportTrace({
							label: 'end',
							traceId,
							methodName,
							traceLabel: label,
							durationMs: Date.now() - startedAt,
							result: summarizeTraceArg(out),
						});
						return out;
					} catch (error) {
						recordImportTrace({
							label: 'error',
							traceId,
							methodName,
							traceLabel: label,
							durationMs: Date.now() - startedAt,
							error: error?.message || String(error),
						});
						throw error;
					}
				};
			};

			const getPromptTitle = (root) => {
				return (root.querySelector('.window-title')?.textContent
					|| root.querySelector('.dialog-title')?.textContent
					|| root.querySelector('[data-title]')?.getAttribute('data-title')
					|| ''
				).trim();
			};

			const isImporterPromptRoot = (root, title) => {
				const promptText = normText([
					title,
					root.id || '',
					String(root.className || ''),
					root.textContent?.slice(0, 500) || '',
				].join(' '));
				return /\b(plutonium|charactermancer|import|choose|select|spells?|features?|proficiencies|proficiency|skills?|tools?|languages?|sizes?|abilities|ability|races?|species|classes|class|subclasses|subclass|feats?|advancements?|advancement)\b/i.test(promptText);
			};

			const getButtonLabel = (button) => (button.textContent || button.value || button.title || button.getAttribute?.('aria-label') || '').toString().trim();

			const findButton = (buttons) => {
				const enabled = buttons.filter((button) => !button.disabled && !button.classList?.contains('disabled'));
				if (!enabled.length) return null;

				const byLabelPreference = [
					// required confirmation/continuation
					(ok) => /^ok$|^okay$|^continue$|^next$|^apply$|^import$|^save$|^done$|^yes$/i.test(ok),
					// explicit yes/no confirmation alternatives
					(ok) => /^accept$|^create$|^add$|^continue anyway$/i.test(ok),
					// fallback path for non-critical optional flows
					(ok) => /^skip$|^skip this$/i.test(ok),
				];

				for (const matcher of byLabelPreference) {
					const primary = enabled.find((button) => matcher(normText(getButtonLabel(button))));
					if (primary) return primary;
				}

				const primary = enabled.find((button) => button.classList.contains('ve-btn-primary'));
				if (primary) return primary;

				const nonCancel = enabled.find((button) => !/^cancel$|^close$/i.test(normText(getButtonLabel(button))));
				if (nonCancel) return nonCancel;

				return enabled[0];
			};

			const fillPromptInputs = (root) => {
				const selects = Array.from(root.querySelectorAll('select')).filter((el) => isVisible(el));
				for (const select of selects) {
					if (!select.value) {
						const options = Array.from(select.options || []);
						const firstEnabled = options.find((option) => option.value != null && option.value !== '');
						if (firstEnabled) {
							select.value = firstEnabled.value;
							select.dispatchEvent(new Event('change', {bubbles: true}));
						}
					}
				}

				const radioGroups = new Map();
				const radios = Array.from(root.querySelectorAll('input[type="radio"]')).filter((el) => isVisible(el));
				for (const radio of radios) {
					const key = radio.name || radio.getAttribute('data-name') || `anon-${radioGroups.size}`;
					if (!radioGroups.has(key)) {
						radioGroups.set(key, []);
					}
					radioGroups.get(key).push(radio);
				}
				for (const group of radioGroups.values()) {
					if (!group.some((radio) => radio.checked)) {
						const firstEnabled = group.find((radio) => !radio.disabled);
						if (firstEnabled) {
							firstEnabled.checked = true;
							firstEnabled.dispatchEvent(new Event('change', {bubbles: true}));
						}
					}
				}
			};

			const automateModal = (root) => {
				const rootId = root.id || null;
				const title = getPromptTitle(root) || root.dataset?.title || null;
				if (!isImporterPromptRoot(root, title)) return false;

				const candidateButtons = Array.from(root.querySelectorAll('button, [role="button"], .ve-btn'));
				const buttons = candidateButtons
					.filter((button, index, all) => button instanceof Element && all.indexOf(button) === index)
					.filter((button) => !button.disabled && !button.classList?.contains('disabled'))
					.filter((button) => normText(getButtonLabel(button)) !== '');
				const visibleButtons = buttons.filter(isVisible);

				const button = findButton(buttons);
				if (!button) {
					const fingerprintNoButton = `${root.tagName}|${rootId || 'no-id'}|${normText(title)}|no-button`;
					const nowNoButton = Date.now();
					const lastNoButton = promptAutomation.handled[fingerprintNoButton] || 0;
					if (nowNoButton - lastNoButton > 1000) {
						promptAutomation.handled[fingerprintNoButton] = nowNoButton;
						recordPromptEvent({
							label: 'visible-importer-root-no-button',
							rootTag: root.tagName.toLowerCase(),
							rootId: rootId,
							promptTitle: title,
							rootClasses: String(root.className || ''),
							buttonCount: buttons.length,
							visibleButtonCount: visibleButtons.length,
							text: root.textContent?.trim?.().slice(0, 240) || null,
						});
					}
					return false;
				}

				const buttonLabel = getButtonLabel(button) || '(unlabeled)';
				const fingerprint = `${root.tagName}|${rootId || 'no-id'}|${normText(title)}|${normText(buttonLabel)}`;
				const now = Date.now();
				const lastSeen = promptAutomation.handled[fingerprint] || 0;
				if (now - lastSeen < 250) return false;
				promptAutomation.handled[fingerprint] = now;

				try {
					fillPromptInputs(root);
					button.click();
					recordPromptEvent({
						label: 'click',
						rootTag: root.tagName.toLowerCase(),
						rootId: rootId,
						promptTitle: title,
						rootClasses: String(root.className || ''),
						choices: buttons.map(getButtonLabel),
						visibleChoices: visibleButtons.map(getButtonLabel),
						selectedButton: buttonLabel,
					});
					return true;
				} catch (error) {
					recordPromptEvent({
						label: 'error',
						rootTag: root.tagName.toLowerCase(),
						rootId: rootId,
						promptTitle: title,
						error: error?.message || String(error),
						rootClasses: String(root.className || ''),
					});
					return false;
				}
			};

			let promptAutomationRunning = false;
			const promptAutomationTick = () => {
				if (promptAutomationRunning) return;
				promptAutomationRunning = true;

				try {
					const promptRoots = Array.from(document.querySelectorAll('.window-app, .dialog, .application.ve-app, .ve-app'))
						.filter(isVisible);
					for (const root of promptRoots) {
						automateModal(root);
					}
				} catch (error) {
					recordPromptEvent({
						label: 'automation-error',
						error: error?.message || String(error),
					});
				} finally {
					promptAutomationRunning = false;
				}
			};

			let automationInterval = null;
			const stopPromptAutomation = () => {
				if (automationInterval) {
					clearInterval(automationInterval);
					automationInterval = null;
				}
				promptAutomation.enabled = false;
				recordPromptEvent({
					label: 'stopped',
					durationMs: Date.now() - promptAutomation.startedAt,
				});
			};

			const getPromptDiagnostics = () => ({
				enabled: promptAutomation.enabled,
				eventCount: promptAutomation.events.length,
				latestEvents: promptAutomation.events.slice(-15),
				events: promptAutomation.events,
			});

			let restoreInputBooleanPrompt = null;

			const installInputBooleanPromptOverride = () => {
				const inputUiUtil = window.InputUiUtil;
				if (!inputUiUtil || typeof inputUiUtil.pGetUserBoolean !== 'function') {
					recordPromptEvent({
						label: 'pGetUserBoolean-hook-skipped',
						reason: 'InputUiUtil.pGetUserBoolean unavailable',
					});
					return null;
				}

				const originalPrompt = inputUiUtil.pGetUserBoolean;
				const wrappedPrompt = async function (...args) {
					const options = args?.[0] || {};
					const title = normText(options.title || '');
					const descriptionRaw = (options.htmlDescription || options.description || options.text || '').toString();
					const description = normText(descriptionRaw.replace(/<[^>]*>/g, ' '));
					if (title === 'ability scores?' && description.includes('apply ability score modifications')) {
						recordPromptEvent({
							label: 'ability-score-confirmation-intercepted',
							promptTitle: options.title || '',
							description: options.htmlDescription || options.description || options.text || null,
						});
						return true;
					}
					return originalPrompt.apply(this, args);
				};

				inputUiUtil.pGetUserBoolean = wrappedPrompt;
				return () => {
					if (inputUiUtil && inputUiUtil.pGetUserBoolean === wrappedPrompt) {
						inputUiUtil.pGetUserBoolean = originalPrompt;
					}
				};
			};

			const restoreInputBooleanPromptWrapper = () => {
				if (typeof restoreInputBooleanPrompt !== 'function') return;
				restoreInputBooleanPrompt();
			};

			const finalizeImportResult = (result = {}) => {
				restoreInputBooleanPromptWrapper();
				restoreInputBooleanPrompt = null;
				stopPromptAutomation();
				return {
					...result,
					promptAutomation: getPromptDiagnostics(),
					importTrace: getImportTraceDiagnostics(),
					selectedImporterPath,
					importStepTimeoutMs,
					summaries,
					failures,
				};
			};

			const buildImportResult = () => finalizeImportResult();

			automationInterval = setInterval(promptAutomationTick, 250);
			restoreInputBooleanPrompt = installInputBooleanPromptOverride();

			const importerCandidates = [
				{
					path: "game.modules.get('plutonium')?.api?.importer",
					importerApi: plutoniumModuleApi?.importer,
				},
				{
					path: 'game.plutonium?.importer',
					importerApi: game.plutonium?.importer,
				},
				{
					path: 'globalThis.plutonium?.importer',
					importerApi: globalThis.plutonium?.importer,
				},
			].map((entry) => {
				const importerApi = entry.importerApi;
				const availableKeys = importerApi && typeof importerApi === 'object'
					? Object.keys(importerApi).sort()
					: [];
				return {
					...entry,
					availableKeys,
					hasImporter: !!importerApi,
				};
			});
			let importerApi = null;
			let selectedImporterPath = null;
			const requiredImporterKeys = ['pGetImporter', 'ActorMultiImportHelper', 'ImportOpts'];

			for (const candidate of importerCandidates) {
				const missingImporterKeys = requiredImporterKeys.filter((key) => typeof candidate.importerApi?.[key] !== 'function');
				if (candidate.importerApi && missingImporterKeys.length === 0) {
					importerApi = candidate.importerApi;
					selectedImporterPath = candidate.path;
					break;
				}
			}

			const moduleApiKeys = plutoniumModuleApi && typeof plutoniumModuleApi === 'object'
				? Object.keys(plutoniumModuleApi).sort()
				: [];
			const globalApiKeys = globalThis.plutonium && typeof globalThis.plutonium === 'object'
				? Object.keys(globalThis.plutonium).sort()
				: [];
			const importerApiKeys = importerApi && typeof importerApi === 'object'
				? Object.keys(importerApi).sort()
				: [];
			const importerCandidateDetails = importerCandidates.map((entry) => {
				const missingImporterKeys = requiredImporterKeys.filter((key) => typeof entry.importerApi?.[key] !== 'function');
				return {
					path: entry.path,
					hasImporter: !!entry.importerApi,
					type: entry.importerApi === undefined ? 'missing' : entry.importerApi === null ? 'null' : typeof entry.importerApi,
					availableKeys: entry.availableKeys,
					missingImporterKeys,
				};
			});
			const missingImporterKeys = importerCandidateDetails.every((it) => it.missingImporterKeys.length === 0)
				? []
				: [...new Set(importerCandidateDetails.flatMap((it) => it.missingImporterKeys))].sort();

			if (!importerApi) {
				failures.push({
					label: 'plutonium',
					error: 'Plutonium importer API unavailable',
					reason: importerCandidateDetails.every((it) => !it.hasImporter)
						? 'Plutonium module API is missing'
						: missingImporterKeys.length
							? `Missing required importer API keys: ${missingImporterKeys.join(', ')}`
							: 'Plutonium importer API path mismatch',
					selectedImporterPath,
					attemptedImporterPaths: importerCandidates.map((it) => it.path),
					importerCandidateDetails,
					moduleApiKeys,
					globalApiKeys,
					importerApiKeys,
					missingImporterKeys,
					availableApiKeys: importerApiKeys,
					promptAutomation: getPromptDiagnostics(),
					importTrace: getImportTraceDiagnostics(),
				});
				return buildImportResult();
			}

			let raceImporter;
			let classImporter;
			try {
				raceImporter = await importerApi.pGetImporter({prop: 'race', isRequired: true});
				classImporter = await importerApi.pGetImporter({prop: 'class', isRequired: true});
			} catch (error) {
				failures.push({
					label: 'plutonium',
					error: `Could not acquire importer endpoints: ${error?.message || String(error)}`,
					promptAutomation: getPromptDiagnostics(),
					importTrace: getImportTraceDiagnostics(),
				});
				return buildImportResult();
			}

			[
				['_pImportEntry_pImportToActor', 'race.importToActor'],
				['_pImportEntry_pFillAbilities', 'race.fillAbilities'],
				['_pImportEntry_pFillSkillsAndTraits', 'race.fillSkillsAndTraits'],
				['_pApplyAllAdditionalSpellsToActor', 'race.applyAdditionalSpells'],
				['_pImportEntry_pFillItems', 'race.fillItems'],
				['_pImportEntry_pImportToActor_pImportStartingEquipment', 'race.importStartingEquipment'],
				['_pImportActorAdditionalFeats', 'race.importAdditionalFeats'],
				['_pImportEntry_pImportToActor_pAddSubEntities', 'race.addSubEntities'],
			].forEach(([methodName, label]) => wrapImporterAsyncMethod(raceImporter, methodName, label));

			[
				['_pImportEntryClass_pImportToActor', 'class.importClassToActor'],
				['_pImportEntrySubclass_pImportToActor', 'class.importSubclassToActor'],
				['_pImportEntryClassSubclass_pImportToActor', 'class.importClassSubclassToActor'],
				['_pImportEntryClass_pGetProficiencyImportMode', 'class.getProficiencyImportMode'],
				['_pImportEntryClass_pGetHpImportMode', 'class.getHpImportMode'],
				['_pImportEntry_pImportToActor_pAddSubEntities', 'class.addSubEntities'],
			].forEach(([methodName, label]) => wrapImporterAsyncMethod(classImporter, methodName, label));

			const getClassForImport = async ({name, source}) => {
				try {
					const hash = window.UrlUtil.URL_TO_HASH_BUILDER.class({name, source});
					const cls = await window.DataLoader.pCacheAndGet('raw_class', source, hash, {isCopy: true});
					if (cls) {
						delete cls.subclasses;
						cls._isFromRivet = true;
					}
					return cls;
				} catch (error) {
					recordImportTrace({
						label: 'import-entity-error',
						prop: 'class',
						name,
						source,
						error: error?.message || String(error),
					});
					return null;
				}
			};

			const getSubclassForImport = async ({name, source, className, classSource}) => {
				try {
					const hash = window.UrlUtil.URL_TO_HASH_BUILDER.subclass({
						name,
						shortName: name,
						source,
						className,
						classSource,
					});
					const sc = await window.DataLoader.pCacheAndGet('raw_subclass', source, hash, {isCopy: true});
					if (sc) sc._isFromRivet = true;
					return sc;
				} catch (error) {
					recordImportTrace({
						label: 'import-entity-error',
						prop: 'subclass',
						name,
						source,
						className,
						classSource,
						error: error?.message || String(error),
					});
					return null;
				}
			};

			const getFromBrew = async (prop, name, source, opts = {}) => {
				if (prop === 'class') {
					const cls = await getClassForImport({name, source});
					if (cls) return cls;
				}
				if (prop === 'subclass') {
					const sc = await getSubclassForImport({
						name,
						source,
						className: opts.className,
						classSource: opts.classSource,
					});
					if (sc) return sc;
				}
				const brew = await window.BrewUtil2.pGetBrewProcessed();
				const list = brew?.[prop] || [];
				const found = list.find((entry) => {
					if (entry?.name !== name || entry?.source !== source) return false;
					if (prop === 'subclass' && opts.className && entry.className !== opts.className) return false;
					if (prop === 'subclass' && opts.classSource && entry.classSource !== opts.classSource) return false;
					return true;
				}) || null;
				if (found && prop === 'class') {
					delete found.subclasses;
					found._isFromRivet = true;
				}
				if (found && prop === 'subclass') found._isFromRivet = true;
				return found;
			};

			const summarizeActor = async (actor, label, expectedType) => {
				const loadedActor = await game.actors.get(actor.id);
				if (!loadedActor) {
					failures.push({
						label,
						error: 'Actor missing after import',
					});
					return;
				}

				const act = loadedActor.toJSON();
				const collectMalformedAdvancementRows = (entries, source, sourceItemName = null) => {
					const out = [];
					for (const [index, it] of (entries || []).entries()) {
						if (!it || typeof it !== 'object') {
							out.push({
								source,
								sourceItem: sourceItemName,
								index,
								reason: 'non-object-row',
							});
							continue;
						}
						if (!it.type) {
							out.push({
								source,
								sourceItem: sourceItemName,
								index,
								reason: 'missing-type',
							});
							continue;
						}
						if (it.type === 'ItemGrant') {
							const hasConfiguredItems = Array.isArray(it.configuration?.items) && it.configuration.items.length > 0;
							const hasAdded = Array.isArray(it.value?.added) && it.value.added.length > 0;
							if (!hasConfiguredItems && !hasAdded) {
								out.push({
									source,
									sourceItem: sourceItemName,
									index,
									type: 'ItemGrant',
									reason: 'item-grant-empty-configuration-and-added',
								});
							}
						}
					}
					return out;
				};

				const collectAdvancementOriginLinks = (value) => {
					if (!value) return [];
					const output = [];
					const walk = (item, rootLabel = 'advancementOrigin') => {
						if (!item) return;
						if (typeof item === 'string') {
							output.push(`${rootLabel}:${item}`);
							return;
						}
						if (Array.isArray(item)) {
							item.forEach((it, idx) => walk(it, `${rootLabel}[${idx}]`));
							return;
						}
						if (typeof item === 'object') {
							const link = item.uuid || item.id || item.itemUuid || item.item?.uuid || item.origin || null;
							if (typeof link === 'string') {
								output.push(`${rootLabel}:${link}`);
								return;
							}
							output.push(`${rootLabel}:${JSON.stringify(item).slice(0, 140)}`);
						}
					};
					walk(value);
					return output;
				};

				const getAdvancementRows = (documentJson) => {
					const advancement = documentJson?.system?.advancement;
					if (Array.isArray(advancement)) return advancement;
					if (advancement && typeof advancement === 'object') return Object.values(advancement);
					return [];
				};

				const actorAdvancementRows = getAdvancementRows(act);
				const itemAdvancementRows = [];
				const items = [];
				const itemMalformedAdvancementRows = [];
				const advancementOriginLinks = [];

				const actorItems = Array.from(loadedActor.items || []);
				for (const itemEntry of actorItems) {
					const item = typeof itemEntry?.toJSON === 'function' ? itemEntry.toJSON() : {
						name: itemEntry?.name || null,
						type: itemEntry?.type || null,
						flags: itemEntry?.flags || {},
						system: itemEntry?.system || null,
					};
					const itemAdvancement = getAdvancementRows(item);
					const itemFlags = item.flags || {};
					itemAdvancementRows.push(...itemAdvancement);
					itemMalformedAdvancementRows.push(...collectMalformedAdvancementRows(itemAdvancement, 'item', item.name || null));
					advancementOriginLinks.push(...collectAdvancementOriginLinks(itemFlags?.dnd5e?.advancementOrigin));
					items.push({
						name: item.name || itemEntry?.name,
						type: item.type || itemEntry?.type,
						flags: itemFlags,
						itemAdvancementRowCount: itemAdvancement.length,
					});
				}

				const malformedAdvancementRows = [
					...collectMalformedAdvancementRows(actorAdvancementRows, 'actor', act.name || act._id || null),
					...itemMalformedAdvancementRows,
				];
				const plutoniumFlags = items.filter((entry) => !!entry.flags?.plutonium).length;
				const hasAdvancementEvidence = actorAdvancementRows.length > 0 || itemAdvancementRows.length > 0 || advancementOriginLinks.length > 0;

				if (!items.length) {
					failures.push({
						label,
						error: 'Actor has no imported items',
					});
				}

				if (!hasAdvancementEvidence) {
					failures.push({
						label,
						error: `No advancement rows for actor (${expectedType})`,
					});
				}

				if (malformedAdvancementRows.length) {
					failures.push({
						label,
						error: `Malformed advancement rows: ${malformedAdvancementRows.length}`,
						count: malformedAdvancementRows.length,
					});
				}

				summaries.push({
					label,
					type: expectedType,
					actorId: act._id,
					actorName: act.name,
					items,
					numberOfItems: items.length,
					actorAdvancementRows: actorAdvancementRows.length,
					itemAdvancementRows: itemAdvancementRows.length,
					advancementOriginLinks: [...new Set(advancementOriginLinks)],
					malformedAdvancementRows,
					plutoniumItemFlags: plutoniumFlags,
				});
			};

			const toActor = async (name) => {
				const actor = await Actor.create({
					name,
					type: 'character',
				});
				if (!actor) {
					throw new Error(`Could not create actor ${name}`);
				}
				return actor;
			};

			const getActorItemCount = (actor) => {
				if (!actor) {
					return null;
				}
				if (typeof actor.items?.size === 'number') {
					return actor.items.size;
				}
				if (actor.items?.contents) {
					try {
						return actor.items.contents.length;
					} catch {
						// ignore
					}
				}
				if (Array.isArray(actor.items)) {
					return actor.items.length;
				}

				const actorJson = actor.toJSON?.();
				if (Array.isArray(actorJson?.items)) {
					return actorJson.items.length;
				}

				return null;
			};

			const collectImportDiagnostics = async ({label, actor, elapsedMs}) => {
				const actorToJson = actor?.toJSON?.();
				const actorSnapshot = actor ? {
					actorId: actor._id || actor.id || actorToJson?.id || null,
					actorName: actor.name || actorToJson?.name || null,
					actorType: actor.type || actorToJson?.type || null,
					actorItemCount: getActorItemCount(actor),
				} : null;

				const actorCollection = game?.actors;
				const totalActorCount = typeof actorCollection?.size === 'number'
					? actorCollection.size
					: Array.isArray(actorCollection?.contents)
						? actorCollection.contents.length
						: null;

				const activeApplications = [];
				if (window.ui?.windows) {
					for (const [appId, app] of Object.entries(window.ui.windows)) {
						const appElement = app?.element;
						activeApplications.push({
							key: appId,
							id: appElement?.id || null,
							title: app?.title || app?.options?.title || app?.options?.window?.title || null,
							classes: appElement?.className ? String(appElement.className) : null,
							appClass: app?.constructor?.name || null,
							rendered: !!app?.rendered,
							minimized: !!app?.minimized,
						});
					}
				}

				const isVisible = (element) => {
					try {
						const style = window.getComputedStyle(element);
						const rect = element.getBoundingClientRect();
						return style.display !== 'none'
							&& style.visibility !== 'hidden'
							&& Number(style.opacity) > 0
							&& rect.width > 1
							&& rect.height > 1;
					} catch {
						return false;
					}
				};

				const visibleWindowsAndModals = Array.from(document.querySelectorAll('.window-app, .dialog, .application.ve-app, .ve-app'))
					.filter((it) => isVisible(it))
					.map((element) => ({
						id: element.id || null,
						tag: element.tagName?.toLowerCase?.() || null,
						classes: String(element.className || ''),
						title: element.getAttribute('title') || null,
						text: element.textContent?.trim?.().slice(0, 160) || null,
					}));

				return {
					label,
					elapsedMs,
					importStepTimeoutMs,
					selectedImporterPath,
					currentUrl: window.location.href,
					pathname: window.location.pathname,
					totalActorCount,
					actor: actorSnapshot,
					activeApplications,
					visibleWindowsAndModals,
					promptAutomation: getPromptDiagnostics(),
					importTrace: getImportTraceDiagnostics(),
				};
			};

			const withSafeImport = async (label, importCall, actor) => {
				const startedAt = Date.now();
				let timeoutHandle = null;
				const timeoutMarker = {};
				const importPromise = (async () => {
					await importCall();
					return {ok: true};
				})();
				importPromise.catch(() => {});

				const timeoutPromise = new Promise((resolve) => {
					timeoutHandle = setTimeout(() => {
						resolve(timeoutMarker);
					}, importStepTimeoutMs);
				});

				try {
					const result = await Promise.race([importPromise, timeoutPromise]);
					if (result === timeoutMarker) {
						const elapsedMs = Date.now() - startedAt;
						failures.push({
							label,
							error: `Import timed out after ${elapsedMs} ms`,
							diagnostics: await collectImportDiagnostics({
								label,
								actor,
								elapsedMs,
							}),
						});
						return false;
					}

					return true;
				} catch (error) {
					const elapsedMs = Date.now() - startedAt;
					failures.push({
						label,
						error: `Import call failed: ${error?.message || String(error)}`,
						elapsedMs,
					});
					return false;
				} finally {
					if (timeoutHandle) {
						clearTimeout(timeoutHandle);
					}
				}
			};

			const withSafeFinalize = async (label, actorMultiImportHelper, actor) => {
				const startedAt = Date.now();
				try {
					await actorMultiImportHelper.pDoFinalize();
					return true;
				} catch (error) {
					const elapsedMs = Date.now() - startedAt;
					failures.push({
						label,
						error: `Finalize failed: ${error?.message || String(error)}`,
						elapsedMs,
						diagnostics: await collectImportDiagnostics({
							label,
							actor,
							elapsedMs,
						}),
					});
					return false;
				}
			};

			const actorMultiImportHelperFor = (actor) => new importerApi.ActorMultiImportHelper({actor});
			const makeImportOpts = ({actor, actorMultiImportHelper}) => new importerApi.ImportOpts({
				actor,
				actorMultiImportHelper,
				levels,
				filterValues: {},
				isBatched: true,
			});

			const pDoPreCacheImporter = async (importer) => {
				if (typeof importer?.pDoPreCachePack !== 'function') return;
				await importer.pDoPreCachePack({pack: null});
			};

			const doDumpImporterCache = (importer) => {
				if (typeof importer?.doDumpPackCache !== 'function') return;
				importer.doDumpPackCache();
			};

			for (const race of plan.races || []) {
				const actor = await toActor(`VO-race-${race.name}`);
				const raceEnt = await getFromBrew('race', race.name, race.source);
				if (!raceEnt) {
					failures.push({label: `${race.name} (${race.source})`, error: 'Race entity not found in loaded brew'});
					continue;
				}
				const actorMultiImportHelper = actorMultiImportHelperFor(actor);
				const importOpts = makeImportOpts({
					actor,
					actorMultiImportHelper,
				});
				await pDoPreCacheImporter(raceImporter);
				const didImport = await withSafeImport(`race:${race.name}|${race.source}`, async () => {
					await raceImporter.pImportEntry(raceEnt, importOpts);
				}, actor);
				doDumpImporterCache(raceImporter);
				if (!didImport) {
					return buildImportResult();
				}
				const didFinalize = await withSafeFinalize(`race:${race.name}|${race.source}`, actorMultiImportHelper, actor);
				if (!didFinalize) {
					return buildImportResult();
				}
				await summarizeActor(actor, `race:${race.name}|${race.source}`, 'race');
			}

			const packageClassKeys = new Set(
				(plan.classes || []).map((entry) => `${entry.name}|${entry.source}`),
			);

			for (const classEntry of plan.classes || []) {
				const actor = await toActor(`VO-class-${classEntry.name}`);
				const clsEnt = await getFromBrew('class', classEntry.name, classEntry.source);
				if (!clsEnt) {
					failures.push({label: `${classEntry.name} (${classEntry.source})`, error: 'Class entity not found in loaded brew'});
					continue;
				}
				const actorMultiImportHelper = actorMultiImportHelperFor(actor);
				const importOpts = makeImportOpts({actor, actorMultiImportHelper});
				await pDoPreCacheImporter(classImporter);
				const didImport = await withSafeImport(`class:${classEntry.name}|${classEntry.source}`, async () => {
					await classImporter.pImportEntry(clsEnt, importOpts);
				}, actor);
				doDumpImporterCache(classImporter);
				if (!didImport) {
					return buildImportResult();
				}
				const didFinalize = await withSafeFinalize(`class:${classEntry.name}|${classEntry.source}`, actorMultiImportHelper, actor);
				if (!didFinalize) {
					return buildImportResult();
				}
				await summarizeActor(actor, `class:${classEntry.name}|${classEntry.source}`, 'class');

				for (const subclass of (plan.subclasses || []).filter((entry) => entry.className === classEntry.name && entry.classSource === classEntry.source)) {
					const subclassEnt = await getFromBrew('subclass', subclass.name, subclass.source, {
						className: subclass.className,
						classSource: subclass.classSource,
					});
					if (!subclassEnt) {
						failures.push({
							label: `subclass:${subclass.name}|${subclass.className}`,
							error: 'Subclass entity not found in loaded brew',
						});
						continue;
					}

					const importOptsSubclass = makeImportOpts({
						actor,
						actorMultiImportHelper,
					});
					await pDoPreCacheImporter(classImporter);
					const didSubclassImport = await withSafeImport(`subclass:${subclass.name}|${subclass.className}`, async () => {
						await classImporter.pImportEntry(subclassEnt, importOptsSubclass);
					}, actor);
					doDumpImporterCache(classImporter);
					if (!didSubclassImport) {
						return buildImportResult();
					}
					const didSubclassFinalize = await withSafeFinalize(`subclass:${subclass.name}|${subclass.className}`, actorMultiImportHelper, actor);
					if (!didSubclassFinalize) {
						return buildImportResult();
					}
					await summarizeActor(actor, `subclass:${subclass.name}|${subclass.className}`, 'subclass');
				}
			}

			for (const subclass of (plan.subclasses || []).filter((entry) => !packageClassKeys.has(`${entry.className}|${entry.classSource}`))) {
				const subclassEnt = await getFromBrew('subclass', subclass.name, subclass.source, {
					className: subclass.className,
					classSource: subclass.classSource,
				});
				if (!subclassEnt) {
					failures.push({
						label: `subclass:${subclass.name}|${subclass.className}`,
						error: 'Subclass entity not found in loaded brew',
					});
					continue;
				}

				let parentClassEnt = await getFromBrew('class', subclass.className, subclass.classSource);

				if (!parentClassEnt) {
					try {
						const raw = await window.DataUtil.class.loadRawJSON();
						if (raw?.class && Array.isArray(raw.class)) {
							parentClassEnt = raw.class.find((entry) => entry.name === subclass.className && entry.source === subclass.classSource) || null;
						}
					} catch (error) {
						failures.push({
							label: `subclass:${subclass.name}|${subclass.className}`,
							error: `Failed to load parent class '${subclass.className}' via DataUtil: ${error?.message || String(error)}`,
						});
						continue;
					}
				}

				if (!parentClassEnt) {
					failures.push({
						label: `subclass:${subclass.name}|${subclass.className}`,
						error: `Parent class '${subclass.className}' (${subclass.classSource}) not resolved from brew or DataUtil`,
					});
					continue;
				}

				const actor = await toActor(`VO-subclass-${subclass.name}`);
				const actorMultiImportHelper = actorMultiImportHelperFor(actor);
				const importOptsClass = makeImportOpts({actor, actorMultiImportHelper});
				await pDoPreCacheImporter(classImporter);
				const didClassImport = await withSafeImport(`subclass:${subclass.name}|${subclass.className}`, async () => {
					await classImporter.pImportEntry(parentClassEnt, importOptsClass);
				}, actor);
				doDumpImporterCache(classImporter);
				if (!didClassImport) {
					return buildImportResult();
				}
				const didClassFinalize = await withSafeFinalize(`subclass:${subclass.name}|${subclass.className}`, actorMultiImportHelper, actor);
				if (!didClassFinalize) {
					return buildImportResult();
				}

				const importOptsSubclass = makeImportOpts({
					actor,
					actorMultiImportHelper,
				});
				await pDoPreCacheImporter(classImporter);
				const didSubclassImport = await withSafeImport(`subclass:${subclass.name}|${subclass.className}`, async () => {
					await classImporter.pImportEntry(subclassEnt, importOptsSubclass);
				}, actor);
				doDumpImporterCache(classImporter);
				if (!didSubclassImport) {
					return buildImportResult();
				}
				const didSubclassFinalize = await withSafeFinalize(`subclass:${subclass.name}|${subclass.className}`, actorMultiImportHelper, actor);
				if (!didSubclassFinalize) {
					return buildImportResult();
				}
				await summarizeActor(actor, `subclass:${subclass.name}|${subclass.className}`, 'subclass');
			}

			return buildImportResult();
		}, {plan, levels: plan.levels || IMPORT_LEVELS, importStepTimeoutMs: FOUNDRY_IMPORT_STEP_TIMEOUT_MS});

		report.importPlan.selectedImporterPath = importResult?.selectedImporterPath || null;
		report.importPlan.importStepTimeoutMs = importResult?.importStepTimeoutMs || FOUNDRY_IMPORT_STEP_TIMEOUT_MS;
		report.promptAutomation = importResult?.promptAutomation || null;
		report.importTrace = importResult?.importTrace || null;
		report.imported = (importResult.summaries || []).map(normalizeReport);
		report.failures.push(...(importResult.failures || []));

		if ((report.failures || []).length) {
			await cleanup(1, `Import workflow recorded ${(report.failures || []).length} failure(s).`);
		}

		await cleanup(0);
	} catch (error) {
		await cleanup(1, error.message || String(error));
	}
};

if (ARGS.has('--help') || ARGS.has('-h')) {
	console.log('Usage: node tools/validate-foundry-plutonium-import.mjs [--preflight]');
	console.log('Environment: FOUNDRY_APP_DIR, FOUNDRY_DATA_DIR, FOUNDRY_WORLD, FOUNDRY_NODE, FOUNDRY_PORT, FOUNDRY_STATIC_PORT, FOUNDRY_IMPORT_REPORT_PATH, FOUNDRY_IMPORT_LEVELS, FOUNDRY_IMPORT_STEP_TIMEOUT_MS, FOUNDRY_USER_ID, FOUNDRY_USER_PASSWORD, CHROMIUM_EXECUTABLE_PATH, PACKAGE_JSON, VO_SOURCE_ID, FOUNDRY_HEADLESS, FOUNDRY_NO_CANVAS');
	process.exit(0);
}

const main = async () => {
	if (ARGS.has('--preflight')) {
		await preflight();
		process.exit(0);
	}

	await preflight();
	const plan = await buildPlaywrightImportPlan();
	await runImport(plan);
};

main().catch((error) => {
	console.error(`BLOCKER: ${error.message || error}`);
	process.exit(1);
});
