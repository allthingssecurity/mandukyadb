# MandukyaDB Remotion Video

This folder contains a Remotion project that renders an explainer video for MandukyaDB including live examples captured from the Python code.

## Prerequisites

- Node.js 18+
- Python 3.10+

## Setup

```
cd remotion
npm install
```

## Preview (interactive)

```
npm run start
```

This runs the Python generator first to create `data/examples.json`, then opens the Remotion player.

## Render to MP4

```
npm run render
```

The output video is written to `remotion/out/mandukyadb.mp4`.

## Regenerating Examples Only

```
python3 ../scripts/generate_examples.py
```

The generator uses the Python API (`MandukyaDB`) to run a small scenario and serializes the outputs for the video.

