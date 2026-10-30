# Project B: Glucose forecast audit

**Question:** Do AI models that forecast low blood sugar beat simple rules? Do they
still work on people, and at times of day, they never trained on?

## Background

A continuous glucose monitor (CGM) is a small sensor worn on the skin. It reads blood
sugar every 5 minutes. People with type 1 diabetes use it to avoid **hypoglycemia** (low
blood sugar), which can cause confusion, seizures, or worse. This is especially dangerous
overnight.

Many papers and apps use AI to predict glucose 30–60 minutes ahead, and the reported
accuracy often looks impressive. But:

- The simplest guess, "in 30 minutes it'll be about what it is now", is already decent,
  so models need to be compared against it.
- Models are often tested on the same people they learned from.
- Average error hides the moments that matter most: lows, nights, after exercise.

## What's already known

A 2026 benchmark (GlucoFM-Bench, 15 datasets, 1,117 people) found that a plain LSTM beat
large pretrained models when there was enough training data. It also found that every
model struggled with type 1 diabetes and with low and high glucose. So the general question
has been studied. A strong student project needs a **narrow angle**, for example:

- Night-time lows after daytime exercise
- People whose data looks different from the training set (age, device, how much they use their pump)
- Whether models are *well calibrated*: when they say "80% chance of a low", does that happen 80% of the time?

## Rough plan (about 14 weeks)

1. **Learn the physiology.** Insulin, carbs, exercise, sensor lag. Use the simglucose
   simulator to watch virtual patients react to meals and insulin.
2. **Get data.** Start with fully open datasets. Some larger ones need a data-use
   agreement and an adult to sign.
3. **Baselines first.** "Stays the same", a straight-line trend, and a simple linear model.
   Write down what "beating the baseline" means *before* training anything.
4. **Train models on the GPU.** An LSTM, a small transformer, a gradient-boosted tree.
5. **Stress-test.** Leave-one-person-out, train on one dataset and test on another,
   night versus day. Score with clinical error grids, not just average error.
6. **Write it up.** Whatever you find, including "the fancy model doesn't help", is the result.

## Decisions that are yours

- Which narrow question to ask
- What counts as a "missed low" and how bad a false alarm is
- Which datasets are fair to compare

## Things to check early

- Science fairs treat human data as human-subjects research. Public, de-identified data
  is usually fine, but may need approval from the fair's review committee first.
- Read each dataset's terms before downloading.

## What you'd learn

Physiology of glucose and insulin, time-series data, model evaluation, and how medical
AI gets tested before people rely on it.
