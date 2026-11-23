import { readDocument, type ServedDocument } from './privacy';

// the terms of use, one text both clients render: the web at `/terms`, beside
// the privacy policy, and the phone's Terms screen
const TERMS = `# Terms of use

Last updated: 24 November 2026

These terms are the agreement between you and the operator of Climbance. By
signing in, you accept them. If you do not accept them, do not sign in.

Climbance is run by Maksim Lunochkin. Write to
[maksim@lunochkin.com](mailto:maksim@lunochkin.com) with any question about
these terms.

## What Climbance is

Climbance is an app for practising algorithmic problem solving, used in a
browser and as an app on your phone. It serves problems, runs the code you
submit against each problem's test cases, and asks you knowledge questions.
From your record it shows your progress and picks what to practise next.

Climbance is free. Nothing in it is paid today. A paid feature, if one comes,
will be described and priced before you can buy it, and these terms will say
what changes.

Climbance is in beta. Features may change, be added or be removed while it is
built.

## Your account

- You sign in through Google or GitHub. The account is yours alone: do not
  share it or sign in as someone else.
- You must be at least 16 years old to use Climbance.
- Keep the Google or GitHub account you sign in with secure. Whoever can sign
  in to that account can sign in to Climbance as you.
- Each account is held to limits on how often it can run code and how much it
  can ask of the app in a given time. The app says so when a limit is reached.

## Using Climbance

The code you submit runs on Climbance's server, in an isolated container with
no network. You agree not to:

- try to escape that container, reach the network from it, or reach the
  server, other users' runs or their data;
- submit code written to harm the server or slow it down for others, such as
  code that mines, floods or probes;
- get around the per-account limits, for example by using several accounts or
  by automating requests;
- copy the problems, the cards, the lessons or the questions out of the app in
  bulk, or republish them;
- use Climbance in a way that breaks the law.

You may try any approach to solving a problem, including one that passes the
tests without being the intended solution. A verdict is evidence about your
own practice, and it ranks you against nobody.

If you find a security weakness, write to the address above rather than use
it. A report made in good faith, that tests against your own account alone and
leaves other users' data unread, is welcome.

## Your content

- The code you write, your answers and your notes stay yours.
- You give the operator the right to store them, to run your code, and to
  process them as the privacy policy describes, so that the app can work and
  show your progress. That right ends when you delete your
  account.
- Feedback you send about Climbance may be used to improve it, with no
  obligation to you.

## Climbance's content

The problems, their test cases and solutions, the cards, the lessons and the
questions belong to the operator. You may use them for your own practice.

The engine's source code is open source under the Apache License 2.0. That
licence covers the code alone, and grants no right to the content above.

## What Climbance does not promise

- The problems, their solutions, the lessons and the questions are written
  with the help of language models and checked, but they may contain mistakes.
  You can ask for a problem to be retired, and say why.
- Ratings, chances to solve, forecasts and the techniques the app names are
  estimates read from your record, not measurements of your ability.
- Climbance does not promise any result outside the app, such as in a contest
  or an exam.
- Climbance may be unavailable at times, for maintenance or because something
  failed. Export your record from the settings if you want a copy of your own.

## Ending

- You can delete your account at any time in the settings. Deleting it erases
  your record, as the privacy policy describes.
- The operator may suspend or close an account that breaks these terms. Where
  the breach allows it, you are told first and given a chance to stop.
- If Climbance closes, you are told at least 30 days before, so that you can
  export your record.

## Liability

Climbance is provided free of charge and as it is. To the extent the law
allows, the operator is not liable for indirect loss, lost data or lost
opportunity arising from its use.

Nothing in these terms limits liability for harm caused intentionally or by
gross negligence, or any right that the consumer law of the country where you
live gives you and does not let a contract take away.

## Changes

These terms change when Climbance changes, and the date at the top says when
they last changed. A change that takes away something you rely on is
announced in the app at least 30 days before it applies. If you do not accept
a change, delete your account before it applies.
`;

export const termsOfUse = (text: string = TERMS): ServedDocument => readDocument(text, 'Terms of use');
