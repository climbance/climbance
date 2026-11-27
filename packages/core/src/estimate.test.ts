import { describe, expect, it } from 'vitest';

import { answerResult, canSubmit } from './answer';
import { estimateShown } from './ask';
import { loadSnapshot } from './courses';
import { parseEstimate } from './reply';
import { verdictView, yourAnswer } from './result';
import type { RawQuestion, Snapshot } from './types';

const DRILL: RawQuestion = {
  id: 'cost-1',
  topic: 'prompting',
  sub: 'tokens-context',
  level: 0,
  kind: 'estimate',
  prompt: 'Estimate the cost, in US dollars.',
  format: 'estimate',
  sent: 'Summarise this.',
  given: [{ name: 'price', label: 'Price, $ per million', value: 2.5 }],
  working: ['400 tokens at $2.5 per million'],
  computed: 0.001,
  factor: 2,
  unit: 'US dollars',
  explain: 'Tokens times the price.',
};

const SNAP: Snapshot = {
  format: 6,
  courses: [
    {
      slug: 'ai-eng',
      definition: {
        title: 'AI Engineering',
        pass_ratio: 0.8,
        kinds: ['estimate'],
        topic: [{ slug: 'prompting', tier: 1, title: 'Prompting', subs: ['tokens-context'] }],
      },
      questions: [],
      drills: [DRILL],
    },
  ],
};

const drill = () => loadSnapshot(SNAP).questions[0];
const reply = (text: string) => ({ text, picked: [], guessing: false });

describe('an estimate drill', () => {
  it('is read from the drills beside the questions', () => {
    // an installed app reads `questions` whole, so a drill travels apart
    expect(drill().format).toBe('estimate');
    expect(drill().estimate?.computed).toBe(0.001);
  });

  it('is correct within its factor of the key, either side', () => {
    expect(answerResult(drill(), [], reply('0.0005')).correct).toBe(true);
    expect(answerResult(drill(), [], reply('0.002')).correct).toBe(true);
    expect(answerResult(drill(), [], reply('0.0021')).correct).toBe(false);
    expect(answerResult(drill(), [], reply('0.00049')).correct).toBe(false);
  });

  it('keeps the number it was given, for the factor still to be set', () => {
    expect(answerResult(drill(), [], reply('$1,000')).drill?.estimate).toBe(1000);
  });

  it('takes a trailing ? as a guess', () => {
    const r = answerResult(drill(), [], reply('0.001?'));
    expect([r.correct, r.guess]).toEqual([true, true]);
  });

  it('submits only a positive number', () => {
    expect(canSubmit(drill(), reply('about a cent'))).toBe(false);
    expect(canSubmit(drill(), reply('0'))).toBe(false);
    expect(canSubmit(drill(), reply('2e-3'))).toBe(true);
    expect(parseEstimate('.5')).toBe(0.5);
  });

  it('shows the key, the range and the working after the answer', () => {
    const r = answerResult(drill(), [], reply('0.01'));
    const v = verdictView(r);
    expect(v.head?.text).toBe('✗ Answer: 0.001 US dollars, within ×2.');
    expect(v.explain).toBe('400 tokens at $2.5 per million\n\nTokens times the price.');
    expect(yourAnswer(r)).toEqual({ kind: 'short', you: '0.01', accepted: '0.0005 to 0.002 US dollars' });
  });

  it('states its texts and given values before the answer', () => {
    expect(estimateShown(drill())).toEqual({
      texts: [{ label: 'Sent', text: 'Summarise this.' }],
      given: [{ label: 'Price, $ per million', value: '2.5' }],
    });
  });
});
