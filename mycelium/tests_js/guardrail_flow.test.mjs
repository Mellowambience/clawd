import test from 'node:test';
import assert from 'node:assert/strict';

import { resolveGatewayReply } from '../static/dashboard/guardrail.mjs';

test('gateway flow uses server validator rewrite when invalid', async () => {
    const result = await resolveGatewayReply({
        userMessage: 'create MIST.md on my desktop with a tutorial',
        assistantMessage: "I'm a cloud-based intelligence and cannot access your files.",
        validateFn: async () => ({
            valid: false,
            normalized_message: 'Local runtime guardrail: blocked by validator.',
            violations: ['cloud_limit_contradiction'],
        }),
    });

    assert.equal(result.rewritten, true);
    assert.equal(result.text, 'Local runtime guardrail: blocked by validator.');
    assert.deepEqual(result.violations, ['cloud_limit_contradiction']);
    assert.equal(result.source, 'server_validator');
});

test('gateway flow falls back to client guardrail when validator fails', async () => {
    const result = await resolveGatewayReply({
        userMessage: 'run command: whoami',
        assistantMessage: "I'm cloud-based, so I don't have direct access to your computer.",
        validateFn: async () => {
            throw new Error('validator unavailable');
        },
    });

    assert.equal(result.rewritten, true);
    assert.match(result.text, /Local runtime override/i);
    assert.deepEqual(result.violations, ['client_fallback_guardrail']);
    assert.equal(result.source, 'client_fallback');
});

test('gateway flow passes benign replies through unchanged', async () => {
    const result = await resolveGatewayReply({
        userMessage: 'summarize architecture',
        assistantMessage: 'Use deterministic local handlers plus constrained gateway logic.',
        validateFn: async () => ({
            valid: true,
            normalized_message: 'Use deterministic local handlers plus constrained gateway logic.',
            violations: [],
        }),
    });

    assert.equal(result.rewritten, false);
    assert.equal(result.text, 'Use deterministic local handlers plus constrained gateway logic.');
    assert.deepEqual(result.violations, []);
    assert.equal(result.source, 'server_validator');
});
