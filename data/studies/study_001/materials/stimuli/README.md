# Asch Conformity Experiment - Stimulus Materials

## Overview

This directory contains the stimulus materials for the Asch conformity experiment (Study 001).

## Stimulus Description

The stimuli consist of 18 cards, each displaying:

1. **Standard Line** (left side): A vertical line, typically 10 inches long
2. **Three Comparison Lines** (right side): Three vertical lines labeled A, B, and C, of different lengths

### Trial Types

#### Neutral Trials (6 trials)
- All lines are clearly distinguishable
- Confederates give correct answers
- Used to establish baseline and maintain credibility
- Examples:
  - Standard: 10", Comparison A: 8.5", B: 10", C: 11.5" (Answer: B)
  - Standard: 8", Comparison A: 8", B: 9.5", C: 6.5" (Answer: A)

#### Critical Trials (12 trials)
- All lines are clearly distinguishable (task remains objectively easy)
- Confederates unanimously give the same INCORRECT answer
- The correct answer differs from confederates' answer by 1.5+ inches
- Examples:
  - Standard: 10", Comparison A: 8", B: 12", C: 10" (Correct: C, Confederates say: A or B)
  - Standard: 7", Comparison A: 7", B: 9", C: 5.5" (Correct: A, Confederates say: B or C)

## Design Principles

1. **Task Simplicity**: The correct answer is always obvious (large differences)
2. **Unambiguous Correct Answer**: Differences of 1.5+ inches ensure no perceptual ambiguity
3. **Confederate Unanimity**: All confederates give the same incorrect answer on critical trials
4. **Intermixing**: Critical and neutral trials are interspersed to maintain engagement

## Physical Specifications

- **Card Size**: 18" × 24"
- **Standard Line**: Positioned on left third of card
- **Comparison Lines**: Positioned on right two-thirds, evenly spaced
- **Line Thickness**: 0.25 inches (thick enough to be clearly visible)
- **Viewing Distance**: 10 feet
- **Line Lengths**: Range from 5" to 12"
- **Presentation Duration**: ~5 seconds per card

## Trial Order

The predetermined order of trials is designed to:
1. Start with 2 neutral practice trials
2. Intermix critical and neutral trials to prevent habituation
3. Avoid predictable patterns
4. Maintain experimental control

## Files in This Directory

- `trial_01.json` through `trial_18.json`: Individual trial specifications
- `confederate_script.json`: Pre-determined responses for all confederates
- `trial_order.json`: Fixed sequence of trial presentation

## Usage Notes

- Confederates must be thoroughly trained to deliver responses naturally
- Seating arrangement is critical: naive participant must hear all confederates before responding
- No feedback is given during the experiment
- Post-experiment interviews assess participant awareness and reasoning
